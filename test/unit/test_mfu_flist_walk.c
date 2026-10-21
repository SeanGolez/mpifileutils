#include "common.h"


static int test_mfu_flist_walk_paths(int* argc, char*** argv)
{
    int failures = 0;

    char* path_1 = tree_scenario_1("test_mfu_flist_walk_paths");
    if (!path_1) {
        fprintf(stderr, "Error creating test scenario.\n");
        return 1;
    }
    const char* paths[] = {path_1};

    /* initialize MPI */
    MPI_Init(argc, argv);
    mfu_init();

    mfu_walk_opts_t* walk_opts = mfu_walk_opts_new();
    mfu_file_t* mfu_file = mfu_file_new();
    mfu_flist flist = mfu_flist_new();

    /* walk single path */
    int rc = mfu_flist_walk_paths(1, paths, walk_opts, flist, mfu_file);
    failures += check_int("Walk was successful", rc, 0);

    /* verify flist is correct*/
    mfu_flist_print(flist);

    mfu_flist_free(&flist);
    mfu_file_delete(&mfu_file);
    mfu_walk_opts_delete(&walk_opts);

    /* shut down MPI */
    mfu_finalize();
    MPI_Finalize();

    free(path_1);

    return failures;
}
int main(int argc, char** argv)
{
    int failures = 0;
    
    printf("\nRunning tests for mfu_flist_walk_paths()...\n");
    failures += test_mfu_flist_walk_paths(&argc, &argv);

    if (failures == 0) {
        printf("\nAll mfu_flist_walk.c tests passed.\n");
        return EXIT_SUCCESS;
    }
    printf("\n%d  mfu_flist_walk.c test(s) FAILED.\n", failures);
    return EXIT_FAILURE;
}
