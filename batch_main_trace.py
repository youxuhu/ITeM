from test_executor import TestExecutor

def batch_execute_test():
    """
    批量执行trace
    """
    executor = TestExecutor()
    #生成批量执行的列表
    test_cases = (
        (f'a{i}{j}', f'b{i}{j}')
        for i in range(1, 7)#a1-a6
        for j in range(1, 6)#ax1-ax4
        for k in range(1, 3)#bx1-bx2
    )

    for case_a , function_b in test_cases:
        print(f'Starting test case to record trace {case_a} and {function_b}')
        executor.execute_test_case(case_a, function_b)
        print(f'Finished test case for {case_a} and {function_b}')

if __name__ == '__main__':
    #执行批量执行
    batch_execute_test()
