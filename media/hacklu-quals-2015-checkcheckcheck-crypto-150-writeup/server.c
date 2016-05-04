// compile with `gcc -o server server.c -std=gnu99 -lcrypto -ggdb`

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/sha.h>

// xor b into a
void xor(uint8_t *a, uint8_t *b, size_t len) {
  for (size_t off = 0; off < len; off++) {
    a[off] ^= b[off];
  }
}

// test whether the whole array is zero without leaking timing
bool test_zero_timingsafe(uint8_t *arr, size_t len) {
  uint8_t x = 0;
  for (size_t off = 0; off < len; off++) {
    x = x | arr[off];
  }
  return x == 0;
}

// Hash the password and truncate it. Long salts are good, but what's the point
// of storing such large hashes? It's not like an attacker can bruteforce a
// valid password without knowing the salt.
void hash_password(uint8_t hash[6], const uint8_t salt[32], const char *password) {
  SHA256_CTX c;
  char digest[SHA256_DIGEST_LENGTH];
  if (SHA256_Init(&c) != 1 ||
      SHA256_Update(&c, password, strlen(password)) != 1 ||
      SHA256_Update(&c, salt, 32) != 1 ||
      SHA256_Final(digest, &c) != 1) {
    fputs("unable to hash\n", stderr);
    exit(1);
  }
  memcpy(hash, digest, 6);
}

void rtrim(char *str) {
  for (char *p = str+strlen(str)-1; p>=str; p--) {
    if (!strchr(" \r\n", *p)) break;
    *p = '\0';
  }
}

void handle(int s) {
  alarm(120);

  // Let's handle the socket like a normal terminal or so. Makes the code much
  // nicer. :)
  if (dup2(s, 0)==-1 || dup2(s, 1)==-1) exit(1);
  setbuf(stdout, NULL);

  char password_salt[32];
  char password_hash[6];
  int hashfd = open("correct_hash", O_RDONLY);
  if (read(hashfd, password_salt, 32) != 32 || read(hashfd, password_hash, 6) != 6) {
    fputs("unable to read password hash\n", stderr);
    exit(1);
  }
  close(hashfd);

  bool logged_in = false;
  while (1) {
    // read and parse line
    char line[50];
    if (fgets(line, sizeof(line), stdin) == NULL) return;
    rtrim(line);
    char *cmd = line;
    char *space = strchr(line, ' ');
    if (space != NULL) *space = '\0';
    char *arg = (space != NULL) ? (space + 1) : NULL;

    // handle command
    if (strcmp(cmd, "version") == 0) {
      puts("This is the password-protected flag storage service, version 2.0. Now featuring a cool password login!");
    } else if (strcmp(cmd, "getflag") == 0) {
      if (logged_in) {
        puts("Okay, sure! Let me grab that flag for you.");
        system("cat flag");
        fputs("someone just grabbed the flag! :)\n", stderr);
      } else {
        puts("Hmmmm? You ask for the flag, but you haven't logged in? Please log in first. Sorry for the hassle, but there are evil hackers around, we need to be careful with who we let into the system.");
      }
    } else if (strcmp(cmd, "login") == 0) {
      if (arg == NULL) {
        puts("Uh, sorry, logging in requires a password.");
        continue;
      }
      char input_hash[6];
      hash_password(input_hash, password_salt, arg);

      // check the hash in a timing-safe way: xor it together with the expected hash,
      // then check whether the result is all zeroes in a timing-safe way.
      xor(password_hash, input_hash, 6);
      if (test_zero_timingsafe(password_hash, 6)) {
        logged_in = true;
        puts("Login successful");
      } else {
        printf("Whoops, that didn't work out. You probably mistyped your password, so you should try again. In case you want to debug the problem, here's the difference between the correct hash and the hash of what you entered: ");
        for (int i=0; i<6; i++) printf("%02hhx", password_hash[i]);
        puts("");
      }
    } else if (strcmp(cmd, "quit") == 0) {
      return;
    } else {
      puts("Sorry, I don't know that command. Valid commands:");
      puts("  version - prints the version of the server. very useful for maintenance purposes and stuff.");
      puts("  getflag - prints the flag. only available after password login in version 2.0 to make hacker attacks harder.");
      puts("  login (new in 2.0!) - logs you in so you can use \"getflag\"");
      puts("  quit - close the connection");
      puts("By the way, my source code is available!");
    }
  }
}

// Just forks and invokes handle() for every connection.
int main(void) {
  signal(SIGCHLD, SIG_IGN);

  int s = socket(AF_INET6, SOCK_STREAM, 0);
  if (s == -1) perror("unable to create server socket"), exit(1);
  int yes = 1;
  if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1 ) {
    perror("setsockopt failed");
    return 1;
  }
  struct sockaddr_in6 bind_addr = {
    .sin6_family = AF_INET6,
    .sin6_port = htons(1513)
  };
  if (bind(s, (struct sockaddr *)&bind_addr, sizeof(bind_addr))) perror("unable to bind socket"), exit(1);
  if (listen(s, 0x10)) perror("deaf"), exit(1);

  while (1) {
    int s_ = accept(s, NULL, NULL);
    if (s_ == -1) {
      perror("accept failed, is this bad?"); /* On Error Resume Next */
      continue;
    }
    pid_t child_pid = fork();
    if (child_pid == -1) {
      perror("can't fork! that's bad, I think.");
      close(s_);
      sleep(1);
      continue;
    }
    if (child_pid == 0) close(s), handle(s_), exit(0);
    close(s_);
  }
}
