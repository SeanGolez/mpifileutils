#include "common.h"

static int is_usr_plus_read(const mfu_perms* perms)
{
    return perms != NULL
        && perms->octal == 0
        && perms->usr == 1
        && perms->group == 0
        && perms->other == 0
        && perms->all == 0
        && perms->assume_all == 0
        && perms->plus == 1
        && perms->read == 1
        && perms->write == 0
        && perms->execute == 0
        && perms->capital_execute == 0
        && perms->assignment == 0;
}

static int is_group_minus_execute(const mfu_perms* perms)
{
    return perms != NULL
        && perms->octal == 0
        && perms->usr == 0
        && perms->group == 1
        && perms->other == 0
        && perms->all == 0
        && perms->assume_all == 0
        && perms->plus == 0
        && perms->read == 0
        && perms->write == 0
        && perms->execute == 1
        && perms->capital_execute == 0
        && perms->assignment == 0;
}

static int test_mfu_perms_parse(void)
{
    int failures = 0;

    /* Check that mode string is expectedly considered valid and that the
     * permission struct linked list was filled out as expected. */
    {
        mfu_perms* head = NULL;
        const char modestr[] = "u+r,g-x";
        int valid = mfu_perms_parse(modestr, &head);
        failures += check_int("valid mode string", valid, 1);

        const mfu_perms* second = head != NULL ? head->next : NULL;
        failures += check_int("u+r permission", is_usr_plus_read(head), 1);
        failures += check_int(
            "g-x permission",
            is_group_minus_execute(second),
            1
        );
        failures += check_int(
            "permission list length",
            second != NULL && second->next == NULL,
            1
        );

        mfu_perms_free(&head);
        failures += check_int("permission list freed", head == NULL, 1);
    }

    /* Check that mode string is expectedly considered invalid. */
    {
        mfu_perms* head = NULL;
        const char modestr[] = "u+ry";
        int valid = mfu_perms_parse(modestr, &head);
        failures += check_int("invalid mode string", valid, 0);
        failures += check_int(
            "uninitialized permission struct linked list",
            head == NULL,
            1
        );
    }

    /* Check that mode octal is expectedly considered valid and that the
     * permission struct linked list was filled out as expected. */
    {
        mfu_perms* head = NULL;
        const char modestr[] = "741";
        int valid = mfu_perms_parse(modestr, &head);
        failures += check_int("valid mode octal", valid, 1);

        failures += check_int("using octal mode", head->octal, 1);
        failures += check_int("permission mode 741", head->mode_octal, 481);
        failures += check_int("permission list length", head->next == NULL, 1);

        mfu_perms_free(&head);
        failures += check_int("permission list freed", head == NULL, 1);
    }

    /* Check that mode octal is expectedly considered invalid. */
    {
        mfu_perms* head = NULL;
        const char modestr[] = "080";
        int valid = mfu_perms_parse(modestr, &head);
        failures += check_int("invalid mode octal", valid, 0);
        failures += check_int(
            "uninitialized permission struct linked list",
            head == NULL,
            1
        );
    }

    return failures;
}

int main(void)
{
    int failures = 0;

    failures += test_mfu_perms_parse();

    if (failures == 0) {
        printf("\nAll mfu_flist_chmod.c tests passed.\n");
        return EXIT_SUCCESS;
    }
    printf("\n%d flist_chmod test(s) FAILED.\n", failures);
    return EXIT_FAILURE;
}
