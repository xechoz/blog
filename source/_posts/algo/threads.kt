// multi thread production and consumption

private val lock = ReentrantLock()
private val notFull = lock.newCondition()
private val notEmpty = lock.newCondition()
private val queue = LinkedList<Any>()
private const val MAX_CAPACITY = 10

private fun LinkedList<Any>.isFull(): Boolean {
    return this.size >= MAX_CAPACITY // example capacity
}


fun produce(item: Any) {
    // with lock

    // when not full, produce item

    // when full, wait for consumption

    // notify consumer 

    lock.withLock {
        while (queue.isFull()) {
            notFull.await()
        }

        queue.add(item)
        notEmpty.signal()
    }
}

fun consume(): Any {
    // with lock

    // when is empty, wait for production

    // else, consume item

    lock.withLock {
        while (queue.isEmpty()) {
            notEmpty.await()
        }

        val item = queue.removeFirst()
        notFull.signal()

        return item
    }
}

// simplify, not limit size of producer

fun produce(item: Any) {
    lock.withLock {
        queue.add(item)
        notEmpty.signalAll()
    }
}

fun consume(): Any {
    lock.withLock {
        while (queue.isEmpty()) {
            notEmpty.await()
        }

        val item = queue.removeFirst()
        return item
    }
}

// blocking queue version, same logic encapsulated
class BlockingQueueVersion(private val capacity: Int = 10) {

    private val queue = ArrayBlockingQueue<Any>(capacity)

    // produce, block when full
    fun produce(item: Any) {
        queue.put(item)
    }

    // consume, block when empty
    fun consume(): Any {
        return queue.take()
    }
}

// kotlin coroutine version, channel is the coroutine analog of blocking queue
class CoroutineProducerConsumer(private val capacity: Int = 10) {
    private val channel = Channel<Any>(capacity)

    // produce, suspend when full
    suspend fun produce(item: Any) {
        channel.send(item)
    }

    // consume, suspend when empty
    suspend fun consume(): Any {
        return channel.receive()
    }
}

// usage
suspend fun runProducerConsumer() {
    val pc = CoroutineProducerConsumer(10)
    val producer = launch { repeat(20) { pc.produce(it) } }
    val consumer = launch { repeat(20) { println(pc.consume()) } }
    producer.join()
    consumer.join()
}


fun test() {
    val producerConsumer = BlockingQueueVersion(10)
    val producer = Thread {
        repeat(100) {
            producerConsumer.produce(it)
            println("Produced: $it")
        }
    }

    val consumer = Thread {
        repeat(100) {
            val item = producerConsumer.consume()
            println("Consumed: $item")
        }
    }

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()
}

private val mutex = Mutex()
private val notFull = mutex.newCondition()
private val notEmpty = mutex.newCondition()
private val queue = LinkedList<Any>()

fun produce(item: Any) {
    // with lock

    // while condiction not met, await

    // add item

    // notify consumer
    mutex.withLock {
        while (queue.isFull()) {
            notFull.await()
        }

        queue.add(item)
        notEmpty.signal()
    }
}

fun consume(): Any {
    // with lock

    // while condiction not met, await

    // remove item

    // notify producer

    mutex.withLock {
        while (queue.isEmpty()) {
            notEmpty.await()
        }

        val item = queue.removeFirst()
        notFull.signal()

        return item
    }
}