# Scala notes
---
## Basics


* Evaluation : 
     *  Basic one : take leftmost operator / evaluate its operands / apply the operator to the operands.
     
            (2*pi)*radius
            
            1. (2*3.14)*radius
            2. 6.28*radius
            3. 6.28*10
            4. 62.8
            
    * Call by value : evaluates every function argument once. If call by value terminate then call by name terminate, the opposite is not true i.e. we can terminate using call by value but not call by name. Call by value is used by default because tend to be exponentially faster.


            def test(x : Int, y : Int) = x * x
            
            test(3+4,8)
            test(7,8)
            7*7
            49

    * Call by name : A function argument is not evaluated if the corresponding parameter is unused in the evaluation of the function body. We can force the call by name using "=>" before the type in the definition of a function. 

            def test(x : Int, y : Int) = x * x
            
            test(3+4,8)
            (3+4)*(3+4)
            7*(3+4)
            7*7
            49

* Substitution model : all the evaluation does is reduce an expression to a value. This is formalized in the lambda calculus.

* Tail recursion : [see](http://stackoverflow.com/questions/33923/what-is-tail-recursion). Tail recursive function behave just like regular loops.   

## Synthax 

* Types :
    * `Int` : 32 bits 
    * `Double` : 64 bits
    * `Boolean`

* Boolean expression : 
    * `true` `false`
    * !b
    * b && c
    * b || c
    * \>=,  >,  <,  <=, ==
    * `if` (e1) r1 `else` r2

* When using `val` the call is by value. When using `def` the call is by name : 
    
        val x = 2
        //reduce by value and output y:Int=4
        val y = square(x) 
        //call by name in the sense that the right side is evaluated at each use. Output y:=>Int
        def y = square(x) 

* Function definition : 

        def square(x : Double) = x * x
        

