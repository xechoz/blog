---
title: Functional in Kotlin
date: 2025-06-19 00:56:06
tags:
---


## About

最近 一个月，在用 {% post_link Redux-for-Android %} 写真实的项目。

有些问题，吹 Functianal Programming 的人不会告诉你，只有掉坑了才知道。

## 函数式编程的坑

immutable data，当 业务很复杂，状态层级很深的时候，immutable 的弊端就出来了。
不仅更改深层的状态非常繁琐，另外即使更改一个很小的状态，也会导致整个状态发生变化。
一连串的连锁反映，最终的问题就是，不仅内存，性能也会受影响。
真的是牵一发而动全身，业务逻辑很复杂的时候，很难维护。

举个例子:

```kotlin
// 用户资料页的数据模型
data class UserProfileState(
    val me: User, // 这个用户
    val friends: List<User>, // 好友
    val posts: List<Post> // 帖子
)

// 用户基本信息
data class User(
    val uid: String,
    val name: String,
    val age: Int,
    ...
)

// 用户发的帖子
data class Post(
    val id: String,
    val content: String,
    val user: User,
    val comments: List<Comment>
)

// 帖子下的评论
data class Comment(
    val id: String,
    val content: String,
    val user: User
)
```

实际会用到的几个逻辑, 写起来是这样的:

`class UserProfileModel`

```kotlin
fun addPost(post: Post) {
    setState {
        copy(
            posts = posts + post
        )
    }
}

fun addComment(postId: String, comment: Comment) {
    setState {
        copy(
            posts = posts.map {
                if (it.id == postId) {
                    it.copy(
                        comments = it.comments + comment
                    )
                } else {
                    it
                }
            }
        )
    }
}

// 看到这个缩进，就知道事情不简单了。这个代码读起来已经很复杂了，但是做的事情很简单，就是更新评论。
// 但是，这个代码有个问题，就是每次更新评论，都会导致整个帖子的状态发生变化。
// 虽然这个例子只有两级状态，但是如果状态层级很深，那么这个问题就会很严重。
// 所以，这个代码是有问题的，但是问题也很明显，就是状态层级很深。
fun updateComment(postId: String, comment: Comment) {
    setState {
        copy(
            posts = posts.map {
                if (it.id == postId) {
                    it.copy(
                        comments = it.comments.map {
                            if (it.id == comment.id) {
                                comment
                            } else {
                                it
                            }
                        }
                    )
                } else {
                    it
                }
            }
        )
    }
}
```

## 解决方案

每个数据都带上 'id', 通过 id 缩减 嵌套的 数据类型

```kotlin
// 用户资料页的数据模型
data class UserProfileState(
    val me: UserId, // 这个用户
    val friends: List<UserId>, // 好友
    val posts: List<PostId> // 帖子
)

// 用户基本信息
data class User(
    val uid: UserId,
    val name: String,
    val age: Int,
    ...
)

// 用户发的帖子
data class Post(
    val id: PostId,
    val content: String,
    val user: UserId,
    val comments: List<CommentId>
)

// 帖子下的评论
data class Comment(
    val id: CommentId,
    val content: String,
    val user: UserId
)
```

数据结构的定义 跟之前差别不大。只是用 Id 替换了 目标的数据类型。这样就可以把逻辑 分开，按各自的 类型处理, 例如 可以拆成
ProfileModel, UserModel, PostModel, CommentModel 基本上每个 data 的逻辑 只有一个 Model 负责，
其他的 Model 负责 处理 数据的 转换。

例如 ProfileModel 负责 处理 用户资料页的数据，UserModel 负责 处理 用户的基本信息，PostModel 负责 处理 帖子的信息，CommentModel 负责 处理 评论的信息。不需要像 UserProfileModel 处理全部的 state 逻辑。现在的 UserProfileModel 只需要组合 各个 model

这样的好处是，我们的 数据 state 模型 还是对应 业务的功能的，从 data state 很容易看出来这个业务的核心数据，拆分的只是逻辑。
而 核心 流程 还是在 UserProfileModel, 只是拆分了各自的子数据处理逻辑

## todo

补充更多的 相关理论基础，例如 mongo db 的 懒加载优化：类似MongoDB的投影(projection)机制，减少初始数据量
行业解决方案等，例如 Arrow.kt 怎么解决的深层级的 modify 数据
