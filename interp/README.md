A Lisp-style interpreter

Ti

Buildin Types
--------------
* void.
* boolean: true and false.
* number: integer and float.
* string.
* procedure: compound procedure.
* primitive: primitive procedure.
* list: python list. <nil> is the empty list.
* table: python dict. !TODO!


A bug
------
I wrote this interpreter according SICP.
So this interpreter does not optimize tail recursion since python does not.

example:

```scheme
(define (iter a) (if (= a 0) 0 (iter (- a 1))))
(iter 1000)
```

This example will end up a "RuntimeError: maximum recursion depth exceeded" exception.

This interpreter is used for querying elasticsearch instead of complex computing. The above case will rarely happen. So I may not fix this bug.
