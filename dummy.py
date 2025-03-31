
#!/bin/bash

log_file="simulation.log"  # Change to your actual simulation log file
input_file="lines_to_track.txt"  # File containing lines to monitor
output_file="timing_report.log"

# Ensure input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: Input file '$input_file' not found!"
    exit 1
fi

echo "Monitoring log file: $log_file" > "$output_file"
echo "Tracking lines from: $input_file" >> "$output_file"

declare -A timestamps  # Associative array to store timestamps

# Read lines to track into an array
mapfile -t lines_to_track < "$input_file"

# Monitor log in real-time
tail -F "$log_file" | while read -r line; do
    for key in "${lines_to_track[@]}"; do
        if [[ "$line" == *"$key"* ]]; then
            current_time=$(date +%s)
            echo "Detected '$key' at $(date)" >> "$output_file"
            
            if [[ -v timestamps["$key"] ]]; then
                previous_time=${timestamps["$key"]}
                elapsed_time=$((current_time - previous_time))
                echo "Time since last '$key': $elapsed_time seconds" >> "$output_file"
            fi
            
            timestamps["$key"]=$current_time
        fi
    done
done



// Code your testbench here
// or browse Examples
module test();
  int d, result;
  int a = 2, b = 3;
  
  function mult(input int a, input int b, output int c);
    c = ( a * b) + 2;
    a++;
    $display($time, " FROM FUNC a = %0d, b = %0d, c = %0d", a, b, c);
  endfunction
  
  initial 
    fork
      begin
        #1;
        mult(a, b, d);
        $display("FROM BLK 1");
        $display($time," a = %0d, b = %0d, c = %0d", a, b, d);
      end
      begin
        #2;
        mult(a, b, d);
        $display("FROM BLK 2");
        $display($time, " a = %0d, b = %0d, c = %0d", a, b, d);
      end
    join
endmodule

/* 1 FROM FUNC a = 3, b = 3, c = 8
# FROM BLK 1
# 1 a = 2, b = 3, c = 8
# 2 FROM FUNC a = 3, b = 3, c = 8
# FROM BLK 2
# 2 a = 2, b = 3, c = 8
When we call mult function from blk 1, it will copy global variables a,b to the local variables a,b inside the function. then inside the function a is incremented which is bound to the function only, won't be reflected to the outside world. If we add function automatic - gives same output. we need to define variables with ref keyword for the variables to share the same memory
*/

function automatic mult(ref int a, ref int b, output int c);

/*# 1 FROM FUNC a = 3, b = 3, c = 8
# FROM BLK 1
# 1 a = 3, b = 3, c = 8
# 2 FROM FUNC a = 4, b = 3, c = 11
# FROM BLK 2
# 2 a = 4, b = 3, c = 11
When we use ref keyword, ref arguments will not have any local memory. Whatever variable we have passed while calling the function, to those variables it will point. So, whatever changes you do inside the function, we are doing on the variables we passed as an arguments means the global variables.
*/

task automatic mult(input int a, input int b, output int c);
    #5;
    c = ( a * b) + 2;
    a++;
    $display($time, " FROM FUNC a = %0d, b = %0d, c = %0d", a, b, c);
  endtask
  
 //same result as function automatic only time will vary
 /* # 6 FROM FUNC a = 3, b = 3, c = 8
# FROM BLK 1
# 6 a = 2, b = 3, c = 8
# 7 FROM FUNC a = 3, b = 3, c = 8
# FROM BLK 2
# 7 a = 2, b = 3, c = 8
*/

class pass_by_ref;
  int refe = 2;
  int val = 2;
  
  function automatic int check_ref(ref int r);
    $display("\n---------------PASS BY REFERENCE------------");
    $display($time, " Initial value of REFE = %0d", r);
    r++;
    $display($time, " Final value of REFE = %0d", r);
  endfunction
  
  function int check_val(int v);
    $display("\n---------------PASS BY VALUE------------");
    $display($time, " Initial value of VAL = %0d", v);
    v++;
    $display($time, " Final value of VAL = %0d", v);
  endfunction
  
endclass



module test;
  initial begin
    pass_by_ref h1 = new();
    h1.check_ref(h1.refe);
    h1.check_val(h1.val);
    $display("\n---------------IN MEMORY------------");
    $display($time, " Value of refe after inc = %0d", h1.refe);
    $display($time, " value of val after inc = %0d", h1.val);
  end
endmodule
  
/*# ---------------PASS BY REFERENCE------------
# 0 Initial value of REFE = 2
# 0 Final value of REFE = 3
# 
# ---------------PASS BY VALUE------------
# 0 Initial value of VAL = 2
# 0 Final value of VAL = 3
# 
# ---------------IN MEMORY------------
# 0 Value of refe after inc = 3
# 0 value of val after inc = 2
*/

// Code your testbench here
// or browse Examples
module test();
  task dummy(input int x, string s);
    fork
      begin
        #x;
      end
      begin
        #10;
      end
    join_any
    disable fork;
      $display("%s is disabled at t = %0t", s, $time);
   endtask
      
   initial 
     fork
       begin
         #2;
         dummy(5, "CALL_1");
       end
       begin
         #1;
         dummy(15, "CALL_2");
       end
     join
endmodule
      
/*
1 - #15
 #10 - CALL_1 is diabled at 11 (1 + 10)

2 - #5 - CALL_1 is disabled at 7 (2 + 5)
 #10
    
*/

//Sorting without a.sort() function
class A;
  rand int a[];
  constraint size {a.size == 10;
                   foreach(a[i])
                     a[i] inside {[1:10]};
                  }
  
  function void post_randomize();
    int keyValue;
    int b;
    $display("Array elements ----BEFORE---- sorting = %p", a);

    for(int i = 1; i < 10; i++)
      begin
        keyValue = a[i];
        b = i - 1;
        while(b >= 0 && a[b] > keyValue)
         begin
            a[b + 1] = a[b];
            b = b - 1;
         end
         a[b + 1] = keyValue;
      end
              
    $display("Array elements ----AFTER---- sorting = %p", a);
  endfunction
endclass

module A;
  initial begin
    A h1 = new();
    h1.randomize();
  end
endmodule

//Array elements ----BEFORE---- sorting = '{7, 1, 7, 9, 6, 10, 7, 3, 3, 10}
//Array elements ----AFTER---- sorting = '{1, 3, 3, 6, 7, 7, 7, 9, 10, 10}

//Queue insertion
// Code your testbench here
// or browse Examples
module test;
  int q1[$] = {1, 2, 3};
  int q2[$] = {4, 5};
  
  initial begin
    //with method
    /*foreach(q2[i])
      q1.insert(i+3, q2[i]);*/
    
    
    
    //without method
    foreach(q2[i])
      q1 = {q1, q2[i]};
    $display("Q1 = %p", q1);
        
  end
endmodule
  
 //Queue methods
 //Read last item from the queue
 i = q_int[$];
 
 //Delete last item from the array
 q_int = q_int[0:$-1];
 
 //Delete entire array
 q_int = {};
 q_int.delete();
 
 //Insertion using concatenation
 q_integer = {q_integer[0:1], 30, q_integer[2:$] }; 
 
 //function void insert (int index, qtype item); inserts an item at the index location insert() 
 q_integer.insert(2,30); 
 
 //Delete one element
 q_integer.delete(2); 
 
 //pop_front(), pop_back(), push_front(), push_back()
 
//Static function, function static
//------------------1--------------//
class A;
  static int i;
  
  static function static get();
    int a; //inside function static, local variables behaves static
    
    a++;
    i++; //static function can access static global variables
    $display("a = %d", a);
    $display("i = %d", i);
    
  endfunction
endclass
o/p 
1
1
2
2
3
3

module test;
  initial begin
    A h1, h2; //no object is required to access static function, simply call
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

//------------2---------------//
class A;
  int i;
  
  static function get();
    int a;
    
    a++;
    //i++;
    $display("a = %d", a);
    //$display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

# a = 1
# a = 1
# a = 1
 
//-----------3--------------//
class A;
  int i;
  
  static function get();
    int a;
    
    a++;
    i++;
    $display("a = %d", a);
    $display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

Error: testbench.sv(8): (vlog-2888) Illegal to access non-static property 'i' from a static method.

//-------------4--------------//
class A;
  static int i;
  
  static function get();
    int a;
    
    a++;
    i++;
    $display("a = %d", a);
    $display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

o/p
1
1
1
2
1
3

//----------5------------//
//In function static, to access global class members we have to create an object. If we want to access local variables, obj creation is not mandatory

class A;
  int i;
  
  function static get();
    int a;
    
    a++;
    i++;
    $display("a = %d", a);
    $display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

Fatal error in Function testbench_sv_unit/A::get at testbench.sv line 8

//-------------6-----------//
class A;
  int i;
  
  function static get();
    int a;
    
    a++;
    //i++;
    $display("a = %d", a);
    //$display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

o/p
1
2
3

//------------6---------------//
class A;
  int i;
  
  function static get();
    int a;
    
    a++;
    i++;
    $display("a = %d", a);
    $display("i = %d", i);
    
  endfunction
endclass

module test;
  initial begin
    A h1, h2;
    h1 = new();
    h2 = new();
    h1.get();
    h1.get();
    h2.get();
  end
endmodule

o/p
# a = 1
# i = 1
# a = 2
# i = 2
# a = 3
# i = 1 //since h2 created a new object, a is shared between h1 & h2 not in

//Child & parent
class A;
  int i;
  
  function new ();
    i = 10;
  endfunction
endclass

class child extends A;
  int i;
  
  function new(int i);
    super.new(10);
    this.i = i;
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new(10);
    $display("i = %p", h1);
  end
endmodule

o/p: Error: testbench.sv(13): Number of actuals and formals does not match in function call.
//Since parent is not expecting any argument

class A;
  int i;
  
  function new ();
    i = 10;
  endfunction
endclass

class child extends A;
  int i;
  
  function new(int i);
    super.new();
    this.i = i;
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new(11);
    $display("i = %p", h1);
  end
endmodule

o/p: i = '{i:10, i:11}

class A;
  int i;
  
  function new (int i);
    this.i = i;
  endfunction
endclass

class child extends A;
  int i;
  
  function new(int i);
    super.new(i);
    this.i = 20;
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new(11);
    $display("i = %p", h1);
  end
endmodule

o/p: i = '{i:11, i:20}

class A;
  int i;
  
  function new (int i = 10);
    this.i = i;
  endfunction
endclass

class child extends A;
  int i;
  
  function new();
    i = 20;
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new();
    $display("i = %p", h1);
  end
endmodule

o/p: i = '{i:10, i:20}

class A;
  int i;
  
  function new (int i = 10);
    i = 10; //i is local to function new, we need to write this.i to access class variable i
  endfunction
endclass

class child extends A;
  int i;
  
  function new();
    i = 20; //this is class variable i
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new();
    $display("i = %p", h1);
  end
endmodule

o/p: i = '{i:0, i:20}

class A;
  int i;
  
  function new ();
    i = 10; 
  endfunction
endclass

class child extends A;
  int i;
  
  function new();
    i = 20; 
  endfunction
endclass

module test;
  initial begin
    child h1;
    h1 = new();
    $display("i = %p", h1);
  end
endmodule

o/p: i = '{i:10, i:20}

//Polymorphism
class A;
  virtual task send();
    $display("IN PARENT CLASS");
  endtask
endclass

class child extends A;
  virtual task send();
    $display("IN CHILD CLASS");
  endtask
endclass

module test;
  initial begin
 A P_h;
    child C_h;
    P_h = new();
    C_h = new();
    
    P_h = C_h;
    P_h.send();
  end
endmodule

o/p: IN CHILD CLASS

class A;
  task send();
    $display("IN PARENT CLASS");
  endtask
endclass

class child extends A;
  virtual task send();
    $display("IN CHILD CLASS");
  endtask
endclass

module test;
  initial begin
 A P_h;
    child C_h;
    P_h = new();
    C_h = new();
    
    P_h = C_h;
    P_h.send();
  end
endmodule

o/p: IN PARENT CLASS

class A;
  virtual task send();
    $display("IN PARENT CLASS");
  endtask
endclass

class child_1 extends A;
  virtual task send();
    $display("IN CHILD-1 CLASS");
  endtask
endclass

class child_2 extends A;
  virtual task send();
    $display("IN CHILD-2 CLASS");
  endtask
endclass

module test;
  initial begin
 A P_h;
    child_1 C1_h;
    child_2 C2_h;
    C1_h = new();
    C2_h = new();
    
    P_h = C1_h;
    C1_h = C2_h;
    P_h.send();
  end
endmodule

o/p: Error: testbench.sv(28): (vlog-13216) Illegal assignment to type 'class testbench_sv_unit::child_1' from type 'class testbench_sv_unit::child_2': Types are not assignment compatible.

class A;
  virtual task send();
    $display("IN PARENT CLASS");
  endtask
endclass

class child_1 extends A;
  virtual task send();
    $display("IN CHILD-1 CLASS");
  endtask
endclass

class child_2 extends child_1;
  task send();
    $display("IN CHILD-2 CLASS");
  endtask
endclass

module test;
  initial begin
 A P_h;
    child_1 C1_h;
    child_2 C2_h;
    C1_h = new();
    C2_h = new();
    
    P_h = C1_h;
    C1_h = C2_h;
    P_h.send();
  end
endmodule

o/p: IN CHILD-1 CLASS

class A;
  virtual task send();
    $display("IN PARENT CLASS");
  endtask
endclass

class child_1 extends A;
  virtual task send();
    $display("IN CHILD-1 CLASS");
  endtask
endclass

class child_2 extends child_1;
  task send();
    $display("IN CHILD-2 CLASS");
  endtask
endclass

module test;
  initial begin
 A P_h;
    child_1 C1_h;
    child_2 C2_h;
    C1_h = new();
    C2_h = new();
    
    //P_h = C1_h;
    C1_h = C2_h;
    P_h.send();
  end
endmodule

o/p: Fatal error, since parent handle is not pointing to any object

class A;
  int i = 10;
endclass

module test;
  initial begin
    repeat(2)
      begin
        A h1, h2;
        h1 = new();
        h2 = new();
        
        h1.i++;
        h2.i++;
        $display("----h1.i = %0d, h2.i = %0d", h1.i, h2.i);
        h1.i++;
        h2.i++;
        $display("----h1.i = %0d, h2.i = %0d", h1.i, h2.i);
      end
  end
endmodule

o/p:
----h1.i = 11, h2.i = 11
----h1.i = 12, h2.i = 12
----h1.i = 11, h2.i = 11
----h1.i = 12, h2.i = 12

class A;
  int i;
  task xyz (string s);
    fork
      begin
        #(i);
      end
      begin
        #(30);
        $display("in object of %s, 20ns is completed", s);
      end
    join_any
    disable fork;
  endtask
endclass
   
A h1 = new();
A h2 = new();
      
module test;
 initial begin

    h1.i = 5;
    h2.i = 20;
    fork 
        h1.xyz("a1");
        h2.xyz("a2");
    join
    end
endmodule

o/p: No o/p is getting printed //DOUBT?????????

class A #(type T = int, int width = 8);
 T i;
 bit[width-1:0] b;
endclass

A #(int, 8) h1;
A #(real, 16) h2;
A h3;

h1 and h3 object assignment can be done since both have same Type and width datatype. h2 with h3/h1 object assignment cannot be done.

//------------THREADS--------------//
module threads;
  initial 
    begin
      fork
        
        for(int h1 = 0; h1 < 2; h1++)
          begin
            #1 $display($time, "Value of H1 = %g", h1);
          end
        
        for(int h2 = 2; h2 > 0; h2--)
          begin
            #1 $display($time, "Value of H2 = %g", h2);
          end
      join
      
        $display("@%g Outside of FORK-JOIN\n", $time);
        #3 $finish;
    end
endmodule

o/p: 
#1Value of H1 = 0
#1Value of H2 = 2
#2Value of H1 = 1
#2Value of H2 = 1
# @2 Outside of FORK-JOIN

module threads;
  initial 
    begin
      fork
        
        for(int h1 = 0; h1 < 2; h1++)
          begin
            #1 $display($time, "Value of H1 = %g", h1);
          end
        
        for(int h2 = 2; h2 > 0; h2--)
          begin
            #1 $display($time, "Value of H2 = %g", h2);
          end
      join_any
      
        $display("@%g Outside of FORK-JOIN\n", $time);
        #3 $finish;
    end
endmodule

o/p:
# 1Value of H1 = 0
# 1Value of H2 = 2
# 2Value of H1 = 1
# @2 Outside of FORK-JOIN
# 
# 2Value of H2 = 1

module threads;
  initial 
    begin
      fork
        
        for(int h1 = 0; h1 < 2; h1++)
          begin
            #1 $display($time, "Value of H1 = %g", h1);
          end
        
        for(int h2 = 2; h2 > 0; h2--)
          begin
            #1 $display($time, "Value of H2 = %g", h2);
          end
      join_none
      
        $display("@%g Outside of FORK-JOIN\n", $time);
        #3 $finish;
    end
endmodule

o/p: # @0 Outside of FORK-JOIN
# 
# 1Value of H1 = 0
# 1Value of H2 = 2
# 2Value of H1 = 1
# 2Value of H2 = 1

module threads;
  initial 
    begin
      fork
        
        for(int h1 = 0; h1 < 2; h1++)
          begin
            #1 $display($time, "Value of H1 = %g", h1);
          end
        
        for(int h2 = 2; h2 > 0; h2--)
          begin
            #1 $display($time, "Value of H2 = %g", h2);
          end
      join_any
      
      disable fork;
      
        $display("@%g Outside of FORK-JOIN\n", $time);
        #3 $finish;
    end
endmodule

o/p:
# 1Value of H1 = 0
# 1Value of H2 = 2
# 2Value of H1 = 1
# @2 Outside of FORK-JOIN

module threads;
  initial 
    begin
      fork
        
        for(int h1 = 0; h1 < 2; h1++)
          begin
            #1 $display($time, "Value of H1 = %g", h1);
          end
        
        for(int h2 = 2; h2 > 0; h2--)
          begin
            #1 $display($time, "Value of H2 = %g", h2);
          end
      join_none
      
      disable fork;
      
        $display("@%g Outside of FORK-JOIN\n", $time);
        #3 $finish;
    end
endmodule

o/p: # @0 Outside of FORK-JOIN

  

