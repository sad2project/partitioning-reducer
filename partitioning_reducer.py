from collections.abc import Mapping
from typing import TypeVar, Generic, Callable, TypeAlias


def identity(item):
    return item


def addToList(acc, item):
    """
    This is necessary instead of just using `list.append` because we need the list to be returned.
    """
    acc.append(item)
    return acc


GK = TypeVar("GK")  # Grouping Key
RV = TypeVar("RV")  # Reduced Value
Orig = TypeVar("Orig")  # Original Type

KeyExtractor = Callable[[Orig], KV]
Reducer = Callable[[RV, Orig], RV]


class GroupingReducer(Mapping[GK, RV], Generic[Orig, GK, RV]):
    """
    This class works a lot like `groupBy()` in Java's Stream API (I think; I haven't looked in a while).
    Given a function used to pull out the value to group by, It creates a MutableMapping where the keys are the
    values being grouped by. The Mapping's values are a reduction of the values in the group. By default,
    they're simply added into a list. But the combination of a `starter` and `reducer` (combined, they work a lot like
    Java's `Collector`s) allow you to do whatever you want with those values. You can count them, average them, find the
    minimum or maximum, or combine them in some way if they support it.

    The part that makes this class a bit less like `groupBy()` is that it's not necessarily done right away. The class
    gives public access to the `add()` and `addAll()` methods, which allow you to continually add values into it after
    the initial creation.

    When you're done, you can use this as a dictionary of the grouped data, or you can pull out the `data` attribute to
    work with it without the extra delegation step. If you want to get the data out right away in one step, it is
    recommended that you use the `GroupingReducer.groupBy()` class method instead. You never need to work with a
    `GroupingReducer` object, then.

    NOTE: `GroupingReducer` only implements methods of `Mapping` instead of `MutableMapping` because it has a very
    specific way that it inserts data, and it doesn't fit removing data as a part of how it's meant to be used. But, if
    you simply MUST make changes to the data, it's in a dictionary in the `data` attribute. If you intend to continue
    using the `GroupingReducer` after taking its `data`, you should instead use `currentData`, which returns a copy of
    it in its current state.
    """

    def __init__(self,
            initialValues: Iterable[Orig]=[],
            *, groupBy: KeyExtractor=identity,
            reducer: Reducer=addToList,
            starter: Supplier=list):
        """

        :param initialValues: Collection of data to group and reduce
        :param groupBy: Function to extract the key to group by from the original data. By default, it uses the entire
            data object
        :param reducer: Function to combine the new piece of data with the current piece of data being reduced. By
            default, it adds the current piece of data to the list.
        :param starter: Function to create the initial reduced value. For example, if you want a sum, you'd pass in 0.
            If you want a product, you'd pass in 1. By default, it creates an empty list.
        """
        self.data = dict()
        self.key_transform = groupBy
        self.reducer = reducer
        self.starter = starter
        self.addAll(initialValues)

    @classmethod
    def groupBy(cls,
            values,
            *, groupBy: KeyExtractor=identity,
            reducer: Reducer=addToList,
            starter: Supplier=list):
        """
        If you have a pile of data that you want grouped and don't need the GroupingReducer wrapper type, but instead
        just want the grouped data back, use this function. It's a shortcut for creating the GroupingReducer and
        extracting the data from it.
        :param values: Collection of data to group and reduce
        :param groupBy: Function to extract the key to group by from the original data. By default, it uses the entire
            data object
        :param reducer: Function to combine the new piece of data with the current piece of data being reduced. By
            default, it adds the current piece of data to the list.
        :param starter: Function to create the initial reduced value. For example, if you want a sum, you'd pass in 0.
            If you want a product, you'd pass in 1. By default, it creates an empty list.
        :return: Dictionary where the keys are the group key, and the values are the reduced values.
        """
        grouper = GroupingReducer(values, groupBy=groupBy, reducer=reducer, starter=starter)
        return grouper.data

    @classmethod
    def reusable(cls, *, groupBy=identity, reducer=addToList, starter=list):
        """
        Want to use the same kind of `GroupingReducer` with many different datasets without supplying the `groupBy`,
        `reducer`, and `starter` functions multiple times? Do you also want to skip using the `GroupingReducer` object
        directly, and just get the grouped data back? This function is for you. It returns a function that just takes in
        the collection of items to group, creates a `GroupingReducer` that runs that collection through it, and returns
        the calculated dataset.
        :param groupBy: Function to extract the key to group by from the original data. By default, it uses the entire
            data object
        :param reducer: Function to combine the new piece of data with the current piece of data being reduced. By
            default, it adds the current piece of data to the list.
        :param starter: Function to create the initial reduced value. For example, if you want a sum, you'd pass in 0.
            If you want a product, you'd pass in 1. By default, it creates an empty list.
        :return: Function that you can reuse, passing iterables of values into and getting the grouped and reduced
            data out of, using the same grouping and reducing logic each time.
        """
        def function(values):
            return GroupingReducer.groupBy(values, groupBy=groupBy, reducer=reducer, starter=starter)
        return function

    @property
    def currentData(self):
        return self.data.copy()

    def add(self, item):
        """
        Provide data to add to the current collection of grouping and reducing.
        :param item: Data point to group and reduce.
        """
        key = self.key_transform(item)
        try:
            self.data[key] = self.reducer(self.data[key], item)
        except KeyError:
            self.data[key] = self.reducer(self.starter(), item)

    def addAll(self, items):
        """
        Provide collection of data to add to the current collection of grouping and reducing.
        :param items: Collection of data points to group and reduce.
        """
        for item in items:
            self.add(item)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def get(self, key, default=None):
        return self.data.get(key, default=default)

    def __eq__(self, other):
        return self.data == other

    def __ne__(self, other):
        return self.data != other
