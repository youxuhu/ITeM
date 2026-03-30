from test_migrator import TestMigrator

def batch_generate_test_intentions():
    #迁移器
    migrator = TestMigrator()
    
    #生成列表
    test_cases = [
        (f'a{i}{j}', f'b{i}{k}')
        for i in range(1, 7)
        for j in range(1, 6)
        for k in range(1, 3)
    ]

    #进行迁移intentions
    for case_a, function_b in test_cases:
        print(f'Generating test intentions for {case_a} and {function_b}')
        migrator.generate_test_intentions(case_a, function_b)
        print(f'Finished generating test intentions for {case_a} and {function_b}')


if __name__=='__main__':
    batch_generate_test_intentions()
