package test
object helloWorld extends App  
{ 
      

{   /* Apply the Newton method to find one roots of a function */            
	val eps = 1e-4                                    
	
	def f1(x : Double) = 3*x*x-2*x-6                  
	def df1(x : Double) = 6*x-2                    
	
	def Newton(cval: Double,f: Double => Double, df : Double => Double): Double =
			if(f(cval) < eps) cval
			else Newton(cval - f(cval)/df(cval), f, df)
	                                                  
			
	println("Result : "+Newton(10, f1, df1))    
}

{	/* Tail recursive implementation of factorial */    
	def fact(x : Int) : Int =
	{
	  def loop(acc : Int , x : Int) : Int = 
			if (x == 0) acc 
			else loop(acc*x,x-1)
			
	  loop(1,x)
	}
	
	println("Result : "+fact(4))
}

}
