from test_migrator import TestMigrator

def migrate_batch_intentions(ts=1, te=7):
    migrator = TestMigrator()
    #生成列表
    test_case = [
        (f'a{i}{j}', f'b{i}{k}',f'a{i}{l}')
        for i in range(ts, te)
        for j in range(1, 6)
        for k in range(1, 3)
        for l in range(1, 6)
        if j != l#排除相同的程序
    ]
    #迁移intentions
    for source, function, target in test_case:
        print(f'Starting migration of intention from {source} to {target} using function {function}')
        migrator.perform_test_intentions(source, function, target)
        print(f'Finished migration of intention from {source} to {target} using function {function}')



if __name__ == '__main__':
    migrate_batch_intentions(1, 7)
