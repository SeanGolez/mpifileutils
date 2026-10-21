#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>

#include "mfu.h"

/****************************************
 * Test Checking
 ***************************************/

int check_str(const char* label, const char* got, const char* expected);
int check_int(const char* label, const int got, const int expected);

/****************************************
 * File Tree Creation
 ***************************************/

typedef enum TreeEntryType {
    TREE_FILE,
    TREE_DIRECTORY
} EntryType;

typedef struct FileTreeNode {
    char* name;                     /* name of the tree entry */
    EntryType type;                 /* file or directory */
    size_t child_count;             /* number of directory children */
    struct FileTreeNode** children; /* array of pointers to child nodes*/
} TreeNode;

TreeNode* create_tree_node(const char* name, EntryType type);
int add_tree_child(TreeNode *parent, TreeNode *child);
void free_tree(TreeNode* node);
int create_empty_test_tree(TreeNode* node, const char* dest_path, mode_t mode);

/****************************************
 * Various Test Scenarios
 ***************************************/

char* tree_scenario_1(const char* rootpath);

#endif /* COMMON_H */
