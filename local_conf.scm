(connect! "localhost" "9200")
(set-current-index! "testdb")
(set-current-doc-type! "testdiff")
(define (goto-testtest) (set-current-doc-type! "testtest"))
(define (goto-testdiff) (set-current-doc-type! "testdiff"))
