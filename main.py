from pzhe.Scanner import Scanner 

if __name__ == '__main__':
    # For Test
    print("====square_sum.c0=====")
    sc = Scanner('example/square_sum.c0')
    sc.run_scan()
    sc.print_list()
    print("====for2.c0=====")
    sc = Scanner('example/for2.c0')
    sc.run_scan()
    sc.print_list()
    print("====simple.c0=====")
    sc = Scanner('example/simple.c0')
    sc.run_scan()
    sc.print_list()
    