#include "common.h"

/****************************************
 * Test scenarios that will be created under $TEST_TMPDIR
 ***************************************/

/* <rootpath>/
 *   ├── file1
 *   ├── file2
 *   └── subdir1/
 *       ├── file3
 *       └── subdir2/
 *           └── subdir3/
 *               └── file4
 */
char* tree_scenario_1(const char* test_name)
{
    const char* test_tmpdir = getenv("TEST_TMPDIR");
    if (!test_tmpdir) {
        fprintf(stderr, "TEST_TMPDIR environment variable not set\n");
        return NULL;
    }

    int needed = snprintf(NULL, 0, "%s/%s", test_tmpdir, test_name);
    char* full_path = malloc(needed + 1);
    if (!full_path) {
        fprintf(stderr, "Failed to allocate memory for path\n");
        return NULL;
    }
    snprintf(full_path, needed + 1, "%s/%s", test_tmpdir, test_name);

    TreeNode* root = create_tree_node(test_name, TREE_DIRECTORY);
    TreeNode* file1 = create_tree_node("file1", TREE_FILE);
    TreeNode* file2 = create_tree_node("file2", TREE_FILE);
    TreeNode* subdir1 = create_tree_node("subdir1", TREE_DIRECTORY);
    TreeNode* file3 = create_tree_node("file3", TREE_FILE);
    TreeNode* subdir2 = create_tree_node("subdir2", TREE_DIRECTORY);
    TreeNode* subdir3 = create_tree_node("subdir3", TREE_DIRECTORY);
    TreeNode* file4 = create_tree_node("file4", TREE_FILE);

    add_tree_child(root, file1);
    add_tree_child(root, file2);
    add_tree_child(root, subdir1);
    add_tree_child(subdir1, file3);
    add_tree_child(subdir1, subdir2);
    add_tree_child(subdir2, subdir3);
    add_tree_child(subdir3, file4);

    create_empty_test_tree(root, test_tmpdir, 0700);

    free_tree(root);

    return full_path;
}
