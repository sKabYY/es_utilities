(define (gcd a b)
  (if (= a 0)
      b
      (gcd (% b a) a)))
(display (gcd 144 12144))
