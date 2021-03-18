/* tee2.c (2021-03-18) -*-Coding: us-ascii-unix;-*- */

/* tee2 duplicates command outputs to fd=1,2,3,4 that are passed by
   the caller.  Its intended use is to copy command outputs to syslog.
   It copies the stdout to fd=3 and the stderr to fd=4 as well as fd=1
   and fd=2.  It uses fd=3 for both the stdout/stderr when fd=4 is not
   passed.  USAGE: tee2 command-and-arguments...  Usually a shell
   (bash) calls this by redirecting fd=3 and fd=4 to
   process-substitutions.  It looses the exit status of the command,
   and just finishes as the command has properly exited with value=0.
   It passes the signal setting to the command, but it itself ignores
   the signals INT and QUIT to keep pumping outputs forward.  It
   disables the output buffers for immediate printing.  It detects
   termination of the subprocess by a closure of the stdout and the
   stderr.  It assumes the write streams (fd=1,2,3,4) never block.  It
   processes the stderr first and then the stdout, to prioritize
   stderr outputs. */

/* GCC with -std=c99 (for GCC<=4) requires the lines below. */

#define _POSIX_SOURCE 500

#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>
#include <assert.h>
#include <poll.h>
#include <spawn.h>

#define VERSION "2021-03-07"
#define GITHUB "https://github.com/RIKEN-RCCS/gfarm-v2-tools"

extern char **environ;

/* The streams for fd=3 and fd=4.  logout=logerr, when fd=4 is
   missing. */

FILE *logout;
FILE *logerr;

/* Prints a message to the stderr by supplementing with an error
   string. */

void
perror2(char *m, int error)
{
    if (error == 0) {
	fprintf(stderr, "tee2 warning: %s\n", m);
	if (logerr != 0) {
	    fprintf(logerr, "tee2 warning: %s\n", m);
	}
    } else {
	char *s = strerror(error);
	fprintf(stderr, "tee2 error: %s: %s\n", m, s);
	if (logerr != 0) {
	    fprintf(logerr, "tee2 error: %s: %s\n", m, s);
	}
    }
    fflush(0);
}

/* Starts a subprocess and forwards the stdout outputs to fd=1 and
   fd=3 and the stderr outputs to fd=2 and fd=4 (or to fd=3 when fd=4 is
   not passed). */

int
main(int argc, char **argv)
{
    int cc;

    if (argc == 1 || strcmp(argv[1], "--version") == 0) {
	fprintf(stdout, ("tee2 version " VERSION " (See " GITHUB ")\n"));
	exit(1);
    }

    /* Prepare the streams for logging. */

    logout = 0;
    logerr = 0;

    int o_fdset;

    {
	o_fdset = 0;
	int flags3 = fcntl(3, F_GETFD);
	if (flags3 >= 0) {
	    o_fdset |= 1;
	}

	int flags4 = fcntl(4, F_GETFD);
	if (flags4 >= 0) {
	    o_fdset |= 2;
	}
	if ((o_fdset & 1) == 0) {
	    perror2("fd=3 not given", EBADF);
	    exit(1);
	}

	{
	    int fd = ((o_fdset & 2) != 0) ? 4 : 3;
	    logerr = fdopen(fd, "w");
	    if (logerr == 0) {
		perror2("fdopen failed", errno);
		exit(1);
	    }
	    cc = setvbuf(logerr, 0, _IONBF, 0);
	    if (cc != 0) {
		perror2("setvbuf failed", 0);
	    }
	}
	if ((o_fdset & 2) != 0) {
	    logout = fdopen(3, "w");
	    if (logout == 0) {
		perror2("fdopen(3) failed", errno);
		exit(1);
	    }
	    cc = setvbuf(logout, 0, _IONBF, 0);
	    if (cc != 0) {
		perror2("setvbuf failed", 0);
	    }
	} else {
	    logout = logerr;
	}
    }
    assert(logerr != 0 && logout != 0);

    /* Disable buffering on the stdout and the stderr. */

    cc = setvbuf(stdout, 0, _IONBF, 0);
    if (cc != 0) {
	perror2("setvbuf failed", 0);
    }
    cc = setvbuf(stderr, 0, _IONBF, 0);
    if (cc != 0) {
	perror2("setvbuf failed", 0);
    }

    int outs[2], errs[2];
    cc = pipe(outs);
    assert(cc == 0);
    cc = pipe(errs);
    assert(cc == 0);

    /* Block signals while spawning. */

    sigset_t osigmask;

    {
	sigset_t sigmask;

	cc = sigemptyset(&sigmask);
	assert(cc == 0);
	cc = sigaddset(&sigmask, SIGINT);
	assert(cc == 0);
	cc = sigaddset(&sigmask, SIGQUIT);
	assert(cc == 0);
	cc = sigaddset(&sigmask, SIGQUIT);
	assert(cc == 0);

	cc = sigprocmask(SIG_BLOCK, &sigmask, &osigmask);
	assert(cc == 0);
    }

    posix_spawn_file_actions_t actions;
    posix_spawnattr_t attrs;

    {
	cc = posix_spawn_file_actions_init(&actions);
	assert(cc == 0);

	cc = posix_spawn_file_actions_addclose(&actions, outs[0]);
	assert(cc == 0);
	cc = posix_spawn_file_actions_addclose(&actions, errs[0]);
	assert(cc == 0);
	cc = posix_spawn_file_actions_adddup2(&actions, outs[1], 1);
	assert(cc == 0);
	cc = posix_spawn_file_actions_adddup2(&actions, errs[1], 2);
	assert(cc == 0);
	cc = posix_spawn_file_actions_addclose(&actions, outs[1]);
	assert(cc == 0);
	cc = posix_spawn_file_actions_addclose(&actions, errs[1]);
	assert(cc == 0);
	cc = posix_spawn_file_actions_addclose(&actions, 3);
	assert(cc == 0);
	if (o_fdset == 3) {
	    cc = posix_spawn_file_actions_addclose(&actions, 4);
	    assert(cc == 0);
	}
    }

    {
	cc = posix_spawnattr_init(&attrs);
	assert(cc == 0);

	short spawnflags = (POSIX_SPAWN_SETSIGMASK);
	cc = posix_spawnattr_setflags(&attrs, spawnflags);
	assert(cc == 0);
	cc = posix_spawnattr_setsigmask(&attrs, &osigmask);
	assert(cc == 0);
    }

    pid_t pid;
    char **argv1 = argv + 1;
    cc = posix_spawnp(&pid, argv1[0], &actions, &attrs, argv1, environ);
    if (cc != 0) {
	char m[160];
	int error = errno;
	snprintf(m, sizeof(m), "posix_spawn(%s) failed", argv1[0]);
	perror2(m, error);
	exit(1);
    }

    cc = posix_spawn_file_actions_destroy(&actions);
    assert(cc == 0);
    cc = posix_spawnattr_destroy(&attrs);
    assert(cc == 0);

    if (1) {
	struct sigaction ignore;
	memset(&ignore, 0, sizeof(ignore));
	cc = sigemptyset(&ignore.sa_mask);
	assert(cc == 0);
	ignore.sa_handler = SIG_IGN;
	ignore.sa_flags = 0;

	/*cc = sigignore(SIGINT);*/
	/*cc = sigignore(SIGQUIT);*/
	/*cc = sigignore(SIGCHLD);*/

	cc = sigaction(SIGINT, &ignore, 0);
	assert(cc == 0);
	cc = sigaction(SIGQUIT, &ignore, 0);
	assert(cc == 0);

	cc = sigprocmask(SIG_SETMASK, &osigmask, 0);
	assert(cc == 0);
    }

    cc = close(outs[1]);
    assert(cc == 0);
    cc = close(errs[1]);
    assert(cc == 0);

    /* Forward the stdout/stderr. */

    int i_fdset;
    i_fdset = 3;
    while (i_fdset != 0) {
	int timeout = /*indefinite*/ -1;
	struct pollfd fds[2];
	nfds_t nfds;

	nfds = 0;
	if ((i_fdset & 2) != 0) {
	    /*stderr-in*/
	    fds[nfds].fd = errs[0];
	    fds[nfds].events = POLLIN;
	    fds[nfds].revents = 0;
	    nfds++;
	}
	if ((i_fdset & 1) != 0) {
	    /*stdout-in*/
	    fds[nfds].fd = outs[0];
	    fds[nfds].events = POLLIN;
	    fds[nfds].revents = 0;
	    nfds++;
	}

	int cc = poll(fds, nfds, timeout);
	if (cc == -1) {
	    if (errno == EINTR || errno == EAGAIN) {
		continue;
	    }
	    assert(0);
	    return errno;
	} else if (cc == 0) {
	    /* TIMEDOUT! */
	    assert(0);
	} else {
	    assert(cc <= 2);
	    /*FALLTHRU*/
	}
	for (nfds_t i = 0; i < nfds; i++) {
	    int out_or_err = (((i_fdset & 2) != 0) && i == 0) ? 1 : 0;

	    if (fds[i].revents == 0) {
		continue;
	    } else if ((fds[i].revents & (POLLIN)) != 0) {
		char b[BUFSIZ];
		int fd = (i == 0) ? errs[0] : outs[0];
		ssize_t n = read(fd, b, sizeof(b));
		if (n == 0) {
		    i_fdset &= ~(1 << out_or_err);
		    continue;
		}
		assert(n > 0);

		FILE *f0 = (out_or_err == 0) ? stdout : stderr;
		cc = fwrite(b, n, 1, f0);
		assert(cc == 1);

		FILE *f1 = (out_or_err == 0) ? logout : logerr;
		cc = fwrite(b, n, 1, f1);
		assert(cc == 1);
	    } else if ((fds[i].revents & (POLLERR|POLLHUP)) != 0) {
		/* HUP for close event. */
		i_fdset &= ~(1 << out_or_err);
		continue;
	    } else if ((fds[i].revents & (POLLNVAL)) != 0) {
		assert(0);
	    } else {
		assert(0);
	    }

	    /* Repeat poll again, to prioritize stderr. */

	    break;
	}
    }

    int stat;

    while (1) {
	pid_t pidcc = waitpid(pid, &stat, 0);
	if (pidcc != -1) {
	    break;
	} else if (errno == ECHILD) {
	    perror2("waitpid failed", errno);
	    stat = 0;
	    break;
	}
	assert(errno == EINTR);
    }

    /* Return normally as exited -- It needs to fake the status. */

    /*WIFEXITED(stat)*/
    /*WIFCONTINUED(stat)*/
    if (WIFSIGNALED(stat)) {
	char m[160];
	int sig = WTERMSIG(stat);
	snprintf(m, sizeof(m), "%s signaled by %d", argv1[0], sig);
	perror2(m, 0);
    } else if (WIFSTOPPED(stat)) {
	char m[160];
	int sig = WSTOPSIG(stat);
	snprintf(m, sizeof(m), "%s stopped by %d", argv1[0], sig);
	perror2(m, 0);
    }

    int v = WEXITSTATUS(stat);
    exit(v);
}
