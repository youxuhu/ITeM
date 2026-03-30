from batch_main_trace import batch_execute_test
from batch_migrate_intentions import migrate_batch_intentions
from batch_generation_intestions import batch_generate_test_intentions
from batch_migrate_oracles import migrate_batch_oracles


def flow(trace_flag=False, intention_generation_flag=False, intention_migration_flag=False, oracle_migration_flag=False):
    """
    批量处理流程，可以选择是否执行trace、生成intentions、迁移intentions和迁移oracles
    """
    if trace_flag:
        batch_execute_test(1, 7)
    if intention_generation_flag:
        batch_generate_test_intentions(1, 7)
    if intention_migration_flag:
        migrate_batch_intentions(1, 7)
    if oracle_migration_flag:
        migrate_batch_oracles(1, 7)


if __name__ == '__main__':

    flow(trace_flag=True)
    flow(intention_generation_flag=True)
    flow(intention_migration_flag=True)
    flow(oracle_migration_flag=True)
