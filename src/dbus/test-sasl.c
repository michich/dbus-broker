/*
 * Test SASL Parser
 */

#include <c-macro.h>
#include <stdlib.h>
#include "dbus/sasl.h"

static void test_server_setup(void) {
        _c_cleanup_(sasl_server_deinit) SASLServer sasl = SASL_SERVER_NULL;

        sasl_server_init(&sasl, 1, "0123456789abcdef");
        sasl_server_deinit(&sasl);

        sasl_server_init(&sasl, 0, "0123456789abcdef");
}

static void test_client_setup(void) {
        _c_cleanup_(sasl_client_deinit) SASLClient sasl = SASL_CLIENT_NULL;

        sasl_client_init(&sasl);
        sasl_client_deinit(&sasl);

        sasl_client_init(&sasl);
}

static void test_server_conversations(void) {
        static const char *requests[] = {
                /* test mechanism discovery */
                NULL,
                "\0AUTH",

                /* test basic EXTERNAL authentication */
                NULL,
                "\0AUTH EXTERNAL 31",
                "BEGIN",

                /* test EXTERNAL with invalid uid and retry */
                NULL,
                "\0AUTH EXTERNAL 30",
                "AUTH EXTERNAL 31",
                "BEGIN",

                /* test EXTERNAL with separate DATA */
                NULL,
                "\0AUTH EXTERNAL",
                "DATA 31",
                "BEGIN",

                /* test EXTERNAL with wrong DATA and retry */
                NULL,
                "\0AUTH EXTERNAL",
                "DATA 30",
                "AUTH EXTERNAL",
                "DATA 31",
                "BEGIN",

                /* test EXTERNAL with anonymous DATA */
                NULL,
                "\0AUTH EXTERNAL",
                "DATA",
                "BEGIN",

                /* test common fast-path */
                NULL,
                "\0AUTH EXTERNAL",
                "DATA",
                "NEGOTIATE_UNIX_FD",
                "BEGIN",

                /* end */
                NULL,
        };
        static const char *replies[] = {
                NULL,
                "REJECTED EXTERNAL",

                NULL,
                "OK 30313233343536373839616263646566",
                NULL,

                NULL,
                "REJECTED EXTERNAL",
                "OK 30313233343536373839616263646566",
                NULL,

                NULL,
                "DATA",
                "OK 30313233343536373839616263646566",
                NULL,

                NULL,
                "DATA",
                "REJECTED EXTERNAL",
                "DATA",
                "OK 30313233343536373839616263646566",
                NULL,

                NULL,
                "DATA",
                "OK 30313233343536373839616263646566",
                NULL,

                NULL,
                "DATA",
                "OK 30313233343536373839616263646566",
                "AGREE_UNIX_FD",
                NULL,

                NULL,
        };
        _c_cleanup_(sasl_server_deinit) SASLServer sasl = SASL_SERVER_NULL;
        const char *reply;
        size_t n_reply;
        size_t i;
        int r;

        assert(C_ARRAY_SIZE(requests) == C_ARRAY_SIZE(replies));

        for (i = 0; i < C_ARRAY_SIZE(requests); ++i) {
                if (requests[i]) {
                        reply = NULL;
                        n_reply = 0;

                        r = sasl_server_dispatch(&sasl,
                                                 requests[i],
                                                 strlen(requests[i] + 1) + 1,
                                                 &reply,
                                                 &n_reply);
                        assert(!r);

                        if (replies[i]) {
                                assert(n_reply == strlen(replies[i]));
                                assert(strcmp(reply, replies[i]) == 0);
                        } else {
                                assert(!n_reply);
                                assert(!reply);
                                assert(sasl_server_is_done(&sasl));
                        }
                } else {
                        assert(!replies[i]);
                        sasl_server_deinit(&sasl);
                        sasl_server_init(&sasl, 1, "0123456789abcdef");
                }
        }
}

static void test_client_run(void) {
        _c_cleanup_(sasl_client_deinit) SASLClient sasl = SASL_CLIENT_NULL;
        const char *output;
        size_t n_output;
        int r;

        sasl_client_init(&sasl);

        r = sasl_client_dispatch(&sasl, NULL, 0, &output, &n_output);
        assert(!r);
        assert(n_output == 46);
        assert(!memcmp(output, "\0AUTH EXTERNAL\r\nDATA\r\nNEGOTIATE_UNIX_FD\r\nBEGIN", 46));

        r = sasl_client_dispatch(&sasl, "DATA", 4, &output, &n_output);
        assert(!r && !n_output && !output);
        r = sasl_client_dispatch(&sasl, "OK 30313233343536373839616263646566", 35, &output, &n_output);
        assert(!r && !n_output && !output);
        r = sasl_client_dispatch(&sasl, "AGREE_UNIX_FD", 13, &output, &n_output);
        assert(!r && !n_output && !output);

        assert(sasl_client_is_done(&sasl));
}

int main(int argc, char **argv) {
        test_server_setup();
        test_client_setup();
        test_server_conversations();
        test_client_run();
        return 0;
}
