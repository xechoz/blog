// qsort — 标准 Lomuto 分区

fun qsort(arr: IntArray, start: Int = 0, end: Int = arr.size - 1) {
    if (start >= end) return

    val pi = arr.partition(arr[end], start, end)

    qsort(arr, start, pi - 1)
    qsort(arr, pi + 1, end)
}

// 标准 Lomuto 分区，返回 pivot 最终位置
fun IntArray.partition(pivot: Int, start: Int, end: Int): Int {
    var left = start // left 是右分区第一个元素的下标

    // 只遍历到 end - 1，pivot 本身不参与比较
    for (i in start until end) {
        if (this[i] <= pivot) {
            swap(left, i)
            left++
        }
    }

    swap(left, end) // 最后把 pivot 放到正确位置
    return left
}

fun IntArray.swap(i: Int, j: Int) {
    val temp = this[i]
    this[i] = this[j]
    this[j] = temp
}


fun IntArray.qsort(start: Int = 0, end: Int = size -1) {} {
    if (start >= end) return

    val pivot = this[end]
    val pivotIndex = partision(pivot, start, end)
    qsort(start, pivotIndex -1)
    qsort(pivotIndex+1, end)
}

fun IntArray.partision(pivot: Int, start:Int, end: Int): Int {
    var left = start

    for (i in start until end) {
        if (this[i] <= pivot) {
            swap(left, i)
            left++
        }
    }

    swap(left, end) // 最后把 pivot 放到正确位置
    return left
}