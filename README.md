# partitioning-reducer
Class to group/partition data and fold/reduce each group at the same time.

## How to install
I won't be publishing this to PyPI, since it's just one Python file. So, you can either copy the file, or you can install it with
`pip` using:

``pip install git+https://www.github.com/sad2project/partitioning-reducer.git#egg=partitioning_reducer``

## Description
`partitioning_reducer.GroupingReducer` works a lot like `groupBy()` in Java's Stream API (I think; I haven't looked in a while).
Given a function used to pull out the value to group by, It creates a MutableMapping where the keys are the
values being grouped by. The Mapping's values are a reduction of the values in the group. By default,
they're simply added into a list. But the combination of a `starter` and `reducer` (combined, they work a lot like
Java's `Collector`s) allow you to do whatever you want with those values. You can count them, average them, find the
minimum or maximum, or combine them in some way if they support it.

The part that makes this class a bit less like `groupBy()` is that it's not necessarily done right away. The class
gives public access to the `add()` and `addAll()` methods, which allow you to continually add values into it after
the initial creation.

To simply run the algorithm and get the resulting normal dictionary, you can use the `GroupingReducer.groupBy()` class method
that immediately returns the dictionary, allowing you to skip to the end.

`GroupingReducer.reusable()` class method creates a function that creates a new GroupingReducer with the same 'algorithmic'
parts so you can do the same reduction on multiple datasets without having to pass those arguments in over and over.
