---
title: 'Update: Redux for android'
date: 2025-03-25 00:41:22
tags:
    - android
    - mvvm
    - redux
---

## Todo

原来的实现太复杂了，需要一个更简单的方案。

不需要大而全，只需要应对简单的场景。复杂的场景，更适合直接用 Mavericks

先要确定，这个project 需要解决的问题是什么？

1. State 管理，生产，分发，消费。over

消费 是 使用方决定。可以去掉

只留下了两个核心概念:

1. state class

2. state repo

no more

我一直在纠结 要不要这个 empty state interface?

问了 AI，这种写法的名字叫 [Marker interface pattern](https://en.wikipedia.org/wiki/Marker_interface_pattern)
主要有两个作用，

1. 类型约束。如果没有类型，或者任意类型，对应使用者是一个心智负担，因为他每次要看实现才知道是不是使用了对的类型。

2. 为之后扩展 RxState 留下可能性。例如 RxState 添加 一些检查 data immutable 的方法

```kotlin
// empty marker interface
interface RxState 

interface <State: RxState> RxRepo {
    /*
    * 这个写法，可以限制 只能在 Repo 的 实现类，或者 扩展方法 才可以 改数据
    * 如果 需要更 严格的约束，可以改成吧 setState 放到 base class 的 protect 方法
    * 但是 我不想这样做。这样会导致 无法使用 kotlin extension function。
    * 例如 fun FooRepo.bar() {}
    *
    /
    fun RxRepo<State>.setState(reducer: State.() -> State)

    suspend <A: Any> onEach(property: KProperty1<State, A>, action: (A) -> Unit)
}
```

新的实现 [android-kotlin-redux](https://github.com/xechoz/android-kotlin-redux/)。
新的实现去掉了 之前多余 的 logic，ui，module 的抽象。原本是计划写一个更大的 framework，也许是简化版的 mavericks, 更适合个人项目使用的 redux。

但是还没想好，估计造出的轮子也不好用，干脆去掉了.

## 参考

1. [Bloch, Joshua (2008). "Item 37: Use marker interfaces to define types". Effective Java](https://archive.org/details/effectivejava00bloc_0/page/179)