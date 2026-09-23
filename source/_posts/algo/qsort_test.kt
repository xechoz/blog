// qsort_test.kt — 测试用例
// 编译运行: kotlinc qsort.kt qsort_test.kt -include-runtime -d qsort_test.jar && java -jar qsort_test.jar

import kotlin.random.Random
import kotlin.system.exitProcess

fun main() {
    var pass = 0
    var fail = 0

    fun check(name: String, arr: IntArray) {
        val expected = arr.sortedArray()
        qsort(arr)
        if (arr.contentEquals(expected)) {
            pass++
            println("PASS  $name -> ${arr.contentToString()}")
        } else {
            fail++
            println("FAIL  $name -> ${arr.contentToString()}  期望 ${expected.contentToString()}")
        }
    }

    // 1. 手工边界用例
    check("空数组", intArrayOf())
    check("单元素", intArrayOf(5))
    check("两元素升序", intArrayOf(1, 2))
    check("两元素逆序", intArrayOf(2, 1))
    check("已升序", intArrayOf(1, 2, 3, 4, 5))
    check("已降序", intArrayOf(5, 4, 3, 2, 1))
    check("全等", intArrayOf(3, 3, 3))
    check("含重复", intArrayOf(3, 7, 8, 5, 2, 1, 9, 5, 4))
    check("pivot 是最大值", intArrayOf(1, 3, 2, 5))
    check("pivot 是最小值", intArrayOf(1, 5, 4, 3, 2))
    check("负数和零", intArrayOf(-3, 0, 7, -1, 2, 0))

    // 2. 随机数组（固定种子，可复现）
    val rng = Random(42)
    for (n in listOf(0, 1, 2, 3, 10, 100, 1000)) {
        repeat(20) {
            val arr = IntArray(n) { rng.nextInt(-100, 100) }
            val expected = arr.sortedArray()
            qsort(arr)
            if (!arr.contentEquals(expected)) {
                fail++
                println("FAIL  随机 n=$n -> ${arr.contentToString()}  期望 ${expected.contentToString()}")
            } else pass++
        }
        println("PASS  随机数组 n=$n x20")
    }

    // 3. 大数组
    val big = IntArray(100_000) { rng.nextInt() }
    val bigExpected = big.sortedArray()
    qsort(big)
    if (big.contentEquals(bigExpected)) {
        pass++
        println("PASS  随机大数组 n=100000")
    } else {
        fail++
        println("FAIL  随机大数组 n=100000")
    }

    // 4. bug 演示：历史版本必然死循环
    expectStackOverflow("原版（无 base case + return left）") {
        qsortOriginal(intArrayOf(3, 7, 8, 5, 2, 1, 9, 5, 4))
    }
    expectStackOverflow("中间版（只有 base case + return left）") {
        qsortHalfFix(intArrayOf(3, 7, 8, 5, 2, 1, 9, 5, 4))
    }

    // 中间版能终止时，会暴露"丢元素"bug：pivot 在 pi-1，右递归从 pi+1 开始，pi 处的元素被跳过
    val dropCase = intArrayOf(2, 3, 4, 5, 1)
    qsortHalfFix(dropCase)
    val dropExpected = intArrayOf(1, 2, 3, 4, 5)
    if (dropCase.contentEquals(dropExpected)) {
        fail++
        println("FAIL  中间版 [2,3,4,5,1] 居然排对了")
    } else {
        pass++
        println("PASS  中间版 [2,3,4,5,1] -> ${dropCase.contentToString()}（元素被跳过，未排序）")
    }

    println()
    println("结果: $pass 通过, $fail 失败")
    if (fail > 0) exitProcess(1)
}

// 在独立小栈线程里运行，捕获 StackOverflowError，避免污染主线程
fun expectStackOverflow(name: String, block: () -> Unit) {
    var overflow = false
    val t = Thread(null, {
        try {
            block()
        } catch (_: StackOverflowError) {
            overflow = true
        }
    }, name, 512 * 1024)
    t.start()
    t.join(5000)
    if (overflow) {
        println("PASS  $name -> 如预期抛出 StackOverflowError")
    } else {
        println("FAIL  $name -> 没有栈溢出（算法居然跑完了？）")
    }
}

// ---- 历史版本（用于演示 bug，勿用于生产）----

// 原版：无递归终止条件
fun qsortOriginal(arr: IntArray, start: Int = 0, end: Int = arr.size - 1) {
    val pivot = arr[end]
    val partitionIndex = arr.partitionOriginal(pivot, start, end)
    qsortOriginal(arr, start, partitionIndex - 1)
    qsortOriginal(arr, partitionIndex + 1, end)
}

fun IntArray.partitionOriginal(pivot: Int, start: Int, end: Int): Int {
    var left = start
    for (i in start..end) {
        if (this[i] <= pivot) {
            swap(left, i)
            left++
        }
    }
    return left
}

// 中间版：加了 base case，但 partition 返回 left（pivot 在 left-1）
fun qsortHalfFix(arr: IntArray, start: Int = 0, end: Int = arr.size - 1) {
    if (start >= end) return
    val pivot = arr[end]
    val partitionIndex = arr.partitionOriginal(pivot, start, end)
    qsortHalfFix(arr, start, partitionIndex - 1)
    qsortHalfFix(arr, partitionIndex + 1, end)
}
