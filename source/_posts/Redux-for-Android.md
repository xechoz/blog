---
title: Redux-for-Android
date: 2025-03-23 16:08:30
tags:
    - android
    - redux
    - kotlin
---

## About

一个精简的 Redux 库，去掉了一些 Redux 官方实例中冗余的设计

## 基础概念

GUI 开发，通常有3个角色：

state: 描述数据状态
action: 管理 state
view: 消费 state，触发 action 逻辑
换成 Android 开发容易理解的话，就是

state = immutable data class
actions = repository, viewmodel, presenter, service, controller, manager
view = view, activity, fragment
一个简单的 counter 示例：

```kotlin
// state
data class State(
    val count: Int = 0
)

// action
class CounterViewModel {
    privte val stateListeners = mutableList<(State)->Unit>()

    var state = State()
        private set

    fun increment() {
        state = state.copy(count = state.count + 1)

        stateListeners.foreach {
            it(state)
        }
    }

    fun onStateChange(listener: (State)->Unit) {
        stateListeners.add(listener)

        listenter(state)
    }
}

// view
class CounterFrament(viewModel: CounterViewModel) {
    init {
        viewMode.onStateChange {
            counterText =  viewmodel.state.count
        }

        setOnClickListener {
            viewModel.increment()
        }
    }
}
```

因为 Android Architect 里边，把数据层称为 Repository，为了更符合Android 平台的称呼，所以接下来说的 Repsitory = Action。

## 核心

看了上面的示例，就会发现，核心只有两个:

1. immutable data class( = state)
2. Repository( = action)： 管理数据

## 实现

state 是 任意 immutable data class 就可以。不需要另外多余的抽象。

所以把实现的重点放到 Repository

Repository 需要关心:

1. 存储 state
2. 分发 state
3. 更新 state

逻辑的生命周期管理
分发 state，对应就有 接收state，这里是 1:N 的关系，1 个 state 可能有 N 个接收者,  
Repository 作为 state 生产者，定位类似 kotlin flow, 只管分发数据，消费者决定怎么使用数据，
通常只有使用者知道什么时候不需要数据了，所以我们可以把监听数据这部分的生命周期管理交给使用者，这样就可以借助 kotlin coroutine scope，消费者自己管理监听&取消监听数据。

Repository 作为数据容器，action 可能很简单，也可能很复杂，
业务上很可能是需要有 诸如 启动，销毁的流程，但是 RxStateRepository 不知道如何处理，这部分属于不能抽象的部分，只能留给使用方（RxStateRepository 的 子类等）处理

```kotlin

typealias RxState = Any

interface <State: RxState> RxStateRepository {
    // 存储 state，对外 只读
    val state: State

    // 分发 state
    suspend fun <A:Any> onEach(property: KProperty1<State, A>, reducer: (A)->Unit) 

    suspend fun onEach(reducer: (State)->Unit)

    suspend fun asFlow(): Flow<State>()

    // 更新 state，限制 只能在 RxStateRepository 的实现类 或者 \
    extension 方法可用
    // data 是 immutable 的，每次 setState 都是 copy 一个新的数据
    fun RxStateRepository<State>.setState(reducer: State.()->State)
}

```

实现类

```kotlin
class <State: RxState> RxStateRepositoryImpl(initState: State) : RxStateRepository<State> {
    private val stateFlow = mutableStateFlow(initState)
    
    override
    val state: State = stateFlow.value

    fun setState(reducer: State.()->State) {
        stateFlow.value = reducer(state)
    }

    override
    suspend fun onEach() {
         supervisorScope { chilScope ->
            childScope.launch {
                stateFlow.
                .collectLatest(reducer)
            }
        }
    }
}
```

## 使用 Demo

```kotlin
data class CounterState(
    val count:Int = 0
)

class CounterRepository: RxStateRepository(CounterState(0)) {
    fun increment() {
        setState {
            copy( count = count + 1)
        }
    }
}

class CounterView {
    private val counter = CounterRepository()
    private val scope = MainScope()

    init {
        scope.launch {
            counter.onEach(CounterState::count) {
                text = "Click $it"
            }
        }

        setOnClickListener {
            counter.increment()
        }
    }
}

// 结合 ViewModel 使用
class FooViewModel: ViewModel(), 
                    RxStateRepository by RxStateRepositoryImpl(FooState()) {
    fun updateFooToBar(bar: Any) {
        setState {
            copy(foo = bar)
        }
    }
}
```

## 参考

1. [Redux Essentials](https://redux.js.org/tutorials/essentials/part-1-overview-concepts)
2. [Mavericks: Android on Autopilot](https://github.com/airbnb/mavericks)
3. [源码:RxState for Android](https://github.com/xechoz/android-kotlin-redux/tree/master)
