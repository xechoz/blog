---
title: 实现：一种极低成本的Android屏幕适配方式
date: 2025-03-23 14:41:43
tags: 
 - android
 - layout
---

## 实现： 一种极低成本的Android屏幕适配方式

参考 [一种极低成本的Android屏幕适配方式](https://mp.weixin.qq.com/s/d9QCoBP6kV9VSWvVldVVwA?mode=light)

## 单个 Activity 适配

```kotlin
class MainActivity : ComponentActivity() {
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(newBase.createCustomDensityContext())
    }
}
```

## 全局适配

``` kotlin
class MainActivity : ComponentActivity() {
    override fun attachBaseContext(newBase: Context) {
        newBase.setCustomDensity()
        super.attachBaseContext(newBase)
    }
}

class MainApplication: Application() {
    override fun attachBaseContext(base: Context) {
        base.setCustomDensity()
        super.attachBaseContext(base)
    }
}
```

## 只适配 这个 View 及其 子 view

**谨慎使用**，createCustomDensityContext 返回的 context 不是 Activity，
如果 子view 有地方拿 context 当做 Activity 使用就会有问题

```kotlin
class FooView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context.createCustomDensityContext(), attrs)
```

## 实现代码

```kotlin
package com.xechoz.lib

import android.app.Application
import android.content.ComponentCallbacks
import android.content.Context
import android.content.res.Configuration
import android.util.AttributeSet
import android.util.DisplayMetrics
import android.view.ContextThemeWrapper
import android.widget.FrameLayout

/**
 * 以 uiWidthDp 为基准，按比例适配 整个 Layout 里的元素
 *
 * 原理是 用 uiWidthDp 跟实际的屏幕 dp 比例，
 * 计算出新的 density, 替换 DisplayMetrics 的 density
 *
 * usage:
 * 在 xml 布局里用
 * <CustomDensityLayout>
 *     <your view>
 * </CustomDensityLayout>
 *
 * 在自定义 View里用:
 * FooView: BarView(context = context.asDensityContext(your_target_width_dp))
 *
 * 参考：
 * [一种极低成本的Android屏幕适配方式](https://mp.weixin.qq.com/s/d9QCoBP6kV9VSWvVldVVwA?mode=light)
 */


/**
 * 适用  全局适配的 场景
 * 适配 整个 Resources， Activity resources 是共享的，改了一个会全部改掉。
 *
 * // 有些代码使用的 application 获取 resource, 这个也要适配
 * class MainApplication: Application() {
 *     override fun attachBaseContext(base: Context) {
 *         base.setCustomDensity()
 *         super.attachBaseContext(base)
 *     }
 * }
 *
 * // 全部 Activity 都适配。 或者在 BaseActivity
 * class MainActivity : ComponentActivity() {
 *     override fun attachBaseContext(newBase: Context) {
 *         newBase.setCustomDensity()
 *         super.attachBaseContext(newBase)
 *     }
 * }
 */
fun Context.setCustomDensity(uiWidthDp: Int = 360) {
    resources.displayMetrics.setCustomDensity(newCustomDensity(uiWidthDp))
}

/**
 * 创建一个 新的 context 适配 Density.
 *
 * [uiWidthDp] 设计稿屏幕 宽度 的dp，默认 360 dp
 *
 * usage:
 *
 * // 单个 Activity 适配
 * class MainActivity : ComponentActivity() {
 *     override fun attachBaseContext(newBase: Context) {
 *         super.attachBaseContext(newBase.createCustomDensityContext())
 *     }
 * }
 *
 * // 全部 Activity 都换掉
 * class MainActivity : ComponentActivity() {
 *     override fun attachBaseContext(newBase: Context) {
 *         newBase.setCustomDensity()
 *         super.attachBaseContext(newBase)
 *     }
 * }
 *
 * // 只适配 这个 View 及其 子 view
 * // 谨慎使用，createCustomDensityContext 返回的 context 不是 Activity，
 * // 如果 子view 有地方拿 context 当做 Activity 使用就会有问题
 *
 * class FooView @JvmOverloads constructor(
 *     context: Context, attrs: AttributeSet? = null
 * ) : FrameLayout(context.createCustomDensityContext(), attrs)
 *
 * @see setCustomDensity
 */
fun Context.createCustomDensityContext(uiWidthDp: Int = 360): Context {
    val custom = newCustomDensity(uiWidthDp)

    val copyConfiguration = Configuration()
    copyConfiguration.densityDpi = custom.targetDensityDpi
    copyConfiguration.setTo(resources.configuration)

    val copyContext = createConfigurationContext(copyConfiguration)

    val copyMetrics = DisplayMetrics()
    copyMetrics.setTo(resources.displayMetrics)
    copyMetrics.setCustomDensity(custom)

    copyContext.resources.displayMetrics.setTo(copyMetrics)
    return if (this is ContextThemeWrapper) ContextThemeWrapper(copyContext, theme) else copyContext
}

/**
 *
 * 只适配 这个 View 及其 子 view
 * 谨慎使用，createCustomDensityContext 返回的 context 不是 Activity，
 * 如果 子view 有地方拿 context 当做 Activity 使用就会有问题
 *
 */
class CustomDensityLayout @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context.createCustomDensityContext(uiWidthDp), attrs) {
    companion object {
        var uiWidthDp = 360 // 设计稿屏幕 宽度 的dp，默认 360 dp
    }
}

/// private ////
private var nonCompatDensity = 0f
private var nonCompatScaledDensity = 0f

private fun Context.newCustomDensity(toWidthDp: Int): CustomDensity {
    (this as? Application ?: applicationContext as? Application)?.let(::updateNonCompatDensity)

    val targetDensity = 1f * resources.displayMetrics.widthPixels / toWidthDp
    val targetScaleDensity = 1f * targetDensity * (nonCompatScaledDensity / nonCompatDensity)
    val targetDensityDpi = (160 * targetScaleDensity).toInt()

    return CustomDensity(
        targetDensity = targetDensity,
        targetScaledDensity = targetScaleDensity,
        targetDensityDpi = targetDensityDpi
    )
}

private fun updateNonCompatDensity(application: Application) {
    val displayMetrics = application.resources.displayMetrics
    if (nonCompatDensity == 0f) {
        nonCompatDensity = displayMetrics.density
        nonCompatScaledDensity = displayMetrics.scaledDensity

        application.registerComponentCallbacks(object : ComponentCallbacks {
            override fun onConfigurationChanged(newConfig: Configuration) {
                if (newConfig.fontScale > 0) {
                    nonCompatScaledDensity = application.resources.displayMetrics.scaledDensity
                }
            }

            override fun onLowMemory() {
            }
        })
    }
}

private fun DisplayMetrics.setCustomDensity(custom: CustomDensity) {
    density = custom.targetDensity
    scaledDensity = custom.targetScaledDensity
    densityDpi = custom.targetDensityDpi
}

private data class CustomDensity(
    val targetDensity: Float,
    val targetScaledDensity: Float,
    val targetDensityDpi: Int
)
```
