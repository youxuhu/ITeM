from test_migrator import TestMigrator

def migrate_batch_oracles():
    migrator = TestMigrator()
    #生成批量迁移列表
    test_cases = [
        (f'a{i}{j}', f'b{i}{k}', f'a{i}{l}')
        for i in range(1, 7)
        for j in range(1, 6)
        for k in range(1, 3)
        for l in range(1, 6)
        if j != l
    ]
    #迁移oracle
    for source, function, target in test_cases:

        print(f'Migrating oracle from {source} to {target} using function {function}')
        
        migrator.migration_test_oracles(source, function, target, False)

        print(f'Finished migrate oracle from {source} to {target} using function {function}')



if __name__ == "__main__":
    migrate_batch_oracles()
    