#include "common.h"
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

/****************************************
 * File Tree Creation
 ***************************************/

/* Create an entry for the file tree structure */
TreeNode* create_tree_node(const char* name, EntryType type)
{
    TreeNode* new_node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!new_node) {
        return NULL;
    }

    new_node->name = (char *)malloc(sizeof(char) * (strlen(name) + 1));
    if (!new_node->name) {
        free(new_node);
        return NULL;
    }

    strcpy(new_node->name, name);
    new_node->type = type;
    new_node->child_count = 0;
    new_node->children = NULL;

    return new_node;
}

/* Add entry as the child of a parent directory entry */
int add_tree_child(TreeNode *parent, TreeNode *child)
{
    if (!parent || !child || parent->type != TREE_DIRECTORY) {
        return 0;
    }

    size_t new_count = parent->child_count + 1;

    TreeNode **new_children = realloc(parent->children,
                                      new_count * sizeof *new_children);

    if (!new_children) {
        return 0;
    }

    new_children[parent->child_count] = child;
    parent->children = new_children;
    parent->child_count = new_count;

    return 1;
}

/* Free file tree structure from memory */
void free_tree(TreeNode* node) {
    if (!node) {
        return;
    }

    for (size_t i = 0; i < node->child_count; i++) {
        free_tree(node->children[i]);
    }

    free(node->children);
    free(node->name);
    free(node);

}

/* Create the file tree structure on the filesystem */
int create_empty_test_tree(TreeNode* node, const char* dest_path, mode_t mode)
{
    char* full_path;

    if (!node) {
        return 0;
    }

    /* Get the full path */
    full_path = (char *)malloc(sizeof(char) *
                               (strlen(node->name) + strlen(dest_path)) + 2);
    if (!full_path) {
        fprintf(stderr, "Error allocating memory for path\n");
        return 0;
    }

    strcpy(full_path, dest_path);
    strcat(full_path, "/");
    strcat(full_path, node->name);

    /* Create it */
    if (node->type == TREE_DIRECTORY) {
        if (mkdir(full_path, mode) == -1 && errno != EEXIST) {
            fprintf(stderr, "Error creating directory: %s\n", full_path);
            free(full_path);
            return 0;
        }
    } else {
        int fd = open(full_path, O_WRONLY | O_CREAT | O_EXCL, mode);

        if (fd == -1) {
            fprintf(stderr, "Error opening file: %s\n", full_path);
            free(full_path);
            return 0;
        }

        if (close(fd) == -1) {
            fprintf(stderr, "Error closing file: %s\n", full_path);
            free(full_path);
            return 0;
        }
    }

    /* Create all children */
    for (size_t i = 0; i < node->child_count; i++) {
        if (!create_empty_test_tree(node->children[i], full_path, mode)) {
            free(full_path);
            return 0;
        }
    }

    free(full_path);
    return 1;
}

/****************************************
 * Test Checking
 ***************************************/

int check_str(const char* label, const char* got, const char* expected)
{
    if (strcmp(got, expected) == 0) {
        printf("PASS %s\n", label);
        return 0;
    }
    printf("FAIL %s\n  expected %s\n  got      %s\n", label, expected, got);
    return 1;
}

int check_int(const char* label, const int got, const int expected)
{
    if (got == expected) {
        printf("PASS %s\n", label);
        return 0;
    }
    printf("FAIL %s\n  expected %d\n  got      %d\n", label, expected, got);
    return 1;
}