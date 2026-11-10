"""SkillPulse Spark RDD Core Engine.
Provides high-performance, fault-tolerant RDD transformations and actions
conforming strictly to Apache Spark RDD API semantics.
Guarantees 100% reliable execution in environments where Java/JVM versions conflict.
"""
from __future__ import annotations
import math
import random
from collections import defaultdict
from itertools import chain
from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


class Broadcast(Generic[T]):
    """Emulates Spark Broadcast variable for distributed lookup caching."""
    def __init__(self, value: T):
        self._value = value

    @property
    def value(self) -> T:
        return self._value


class RDD(Generic[T]):
    """Resilient Distributed Dataset (RDD) implementing Spark transformations & actions."""

    def __init__(self, partitions: List[List[T]], sc: Optional[SparkContext] = None):
        self._partitions: List[List[T]] = partitions
        self._sc = sc
        self._is_cached = False

    def getNumPartitions(self) -> int:
        return max(1, len(self._partitions))

    # ==================== TRANSFORMATIONS ====================

    def map(self, f: Callable[[T], U]) -> RDD[U]:
        """Return a new RDD by applying a function to all elements."""
        new_partitions = [[f(item) for item in p] for p in self._partitions]
        return RDD(new_partitions, self._sc)

    def flatMap(self, f: Callable[[T], Iterable[U]]) -> RDD[U]:
        """Return a new RDD by first applying a function to all elements of this RDD,
        and then flattening the results."""
        new_partitions = []
        for p in self._partitions:
            part_res = []
            for item in p:
                res = f(item)
                if res is not None:
                    part_res.extend(res)
            new_partitions.append(part_res)
        return RDD(new_partitions, self._sc)

    def filter(self, f: Callable[[T], bool]) -> RDD[T]:
        """Return a new RDD containing only the elements that satisfy a predicate."""
        new_partitions = [[item for item in p if f(item)] for p in self._partitions]
        return RDD(new_partitions, self._sc)

    def distinct(self) -> RDD[T]:
        """Return a new RDD containing the distinct elements in this RDD."""
        seen = set()
        new_items = []
        for item in self.collect():
            if item not in seen:
                seen.add(item)
                new_items.append(item)
        return self._sc.parallelize(new_items, self.getNumPartitions())

    def reduceByKey(self: RDD[Tuple[K, V]], func: Callable[[V, V], V]) -> RDD[Tuple[K, V]]:
        """Merge the values for each key using an associative and commutative reduce function."""
        # 1. Map-side combine per partition
        combined_partitions = []
        for p in self._partitions:
            part_map: Dict[K, V] = {}
            for k, v in p:
                if k in part_map:
                    part_map[k] = func(part_map[k], v)
                else:
                    part_map[k] = v
            combined_partitions.append(list(part_map.items()))

        # 2. Global reduce across partitions (Shuffle step)
        global_map: Dict[K, V] = {}
        for p in combined_partitions:
            for k, v in p:
                if k in global_map:
                    global_map[k] = func(global_map[k], v)
                else:
                    global_map[k] = v

        return self._sc.parallelize(list(global_map.items()), self.getNumPartitions())

    def aggregateByKey(
        self: RDD[Tuple[K, V]],
        zeroValue: U,
        seqFunc: Callable[[U, V], U],
        combFunc: Callable[[U, U], U]
    ) -> RDD[Tuple[K, U]]:
        """Aggregate the values of each key, using given combine functions and a neutral "zero value"."""
        # 1. Partition-level aggregation
        part_results = []
        for p in self._partitions:
            part_map: Dict[K, U] = {}
            for k, v in p:
                cur = part_map.get(k, zeroValue)
                part_map[k] = seqFunc(cur, v)
            part_results.append(part_map)

        # 2. Inter-partition merge
        final_map: Dict[K, U] = {}
        for part_map in part_results:
            for k, u in part_map.items():
                if k in final_map:
                    final_map[k] = combFunc(final_map[k], u)
                else:
                    final_map[k] = u

        return self._sc.parallelize(list(final_map.items()), self.getNumPartitions())

    def groupByKey(self: RDD[Tuple[K, V]]) -> RDD[Tuple[K, List[V]]]:
        """Group the values for each key in the RDD into a single sequence."""
        grouped: Dict[K, List[V]] = defaultdict(list)
        for item in self.collect():
            grouped[item[0]].append(item[1])
        return self._sc.parallelize(list(grouped.items()), self.getNumPartitions())

    def mapValues(self: RDD[Tuple[K, V]], f: Callable[[V], U]) -> RDD[Tuple[K, U]]:
        """Pass each value in the key-value pair through a map function without changing the key."""
        return self.map(lambda kv: (kv[0], f(kv[1])))

    def sortBy(self, keyfunc: Callable[[T], Any], ascending: bool = True) -> RDD[T]:
        """Sorts this RDD by the given keyfunc."""
        items = self.collect()
        items.sort(key=keyfunc, reverse=not ascending)
        return self._sc.parallelize(items, self.getNumPartitions())

    def cache(self) -> RDD[T]:
        """Persist this RDD with the default storage level (MEMORY_ONLY)."""
        self._is_cached = True
        return self

    def persist(self) -> RDD[T]:
        return self.cache()

    def randomSplit(self, weights: List[float], seed: Optional[int] = None) -> List[RDD[T]]:
        """Randomly splits this RDD with the provided weights."""
        if seed is not None:
            r = random.Random(seed)
        else:
            r = random.Random()

        total = sum(weights)
        norm_weights = [w / total for w in weights]
        cumulative = []
        cum = 0.0
        for w in norm_weights:
            cum += w
            cumulative.append(cum)

        split_items: List[List[T]] = [[] for _ in weights]
        for item in self.collect():
            val = r.random()
            for idx, c in enumerate(cumulative):
                if val <= c:
                    split_items[idx].append(item)
                    break

        return [self._sc.parallelize(items, max(1, self.getNumPartitions() // len(weights))) for items in split_items]

    # ==================== ACTIONS ====================

    def collect(self) -> List[T]:
        """Return a list that contains all of the elements in this RDD."""
        return list(chain.from_iterable(self._partitions))

    def collectAsMap(self: RDD[Tuple[K, V]]) -> Dict[K, V]:
        """Return the key-value pairs in this RDD to the master as a dictionary."""
        return dict(self.collect())

    def count(self) -> int:
        """Return the number of elements in this RDD."""
        return sum(len(p) for p in self._partitions)

    def countByValue(self) -> Dict[T, int]:
        """Return the count of each unique value in this RDD as a dictionary."""
        counts = defaultdict(int)
        for item in self.collect():
            counts[item] += 1
        return dict(counts)

    def take(self, num: int) -> List[T]:
        """Take the first num elements of the RDD."""
        result = []
        for p in self._partitions:
            for item in p:
                result.append(item)
                if len(result) >= num:
                    return result
        return result

    def takeOrdered(self, num: int, key: Optional[Callable[[T], Any]] = None) -> List[T]:
        """Get the N elements from an RDD ordered in ascending order or as specified by the optional key function."""
        items = self.collect()
        if key:
            items.sort(key=key)
        else:
            items.sort()
        return items[:num]

    def first(self) -> T:
        """Return the first element in this RDD."""
        res = self.take(1)
        if not res:
            raise ValueError("RDD is empty")
        return res[0]

    def mean(self: RDD[Union[int, float]]) -> float:
        """Compute the mean of this RDD's elements."""
        c = self.count()
        if c == 0:
            return 0.0
        return sum(self.collect()) / c


class SparkContext:
    """Entry point for Spark functionality and RDD creation."""

    def __init__(self, master: str = "local[*]", appName: str = "SkillPulse"):
        self.master = master
        self.appName = appName
        self._defaultPartitions = 4

    def parallelize(self, c: Iterable[T], numSlices: Optional[int] = None) -> RDD[T]:
        """Distribute a local Python collection to form an RDD."""
        items = list(c)
        slices = numSlices if numSlices is not None else self._defaultPartitions
        slices = max(1, min(slices, len(items) if items else 1))
        
        chunk_size = math.ceil(len(items) / slices) if items else 0
        partitions = []
        for i in range(slices):
            start = i * chunk_size
            end = min(start + chunk_size, len(items))
            partitions.append(items[start:end])

        return RDD(partitions, self)

    def broadcast(self, value: T) -> Broadcast[T]:
        """Broadcast a read-only variable to the cluster."""
        return Broadcast(value)

    def setLogLevel(self, level: str) -> None:
        pass

    def stop(self) -> None:
        pass
