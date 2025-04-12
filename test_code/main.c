#include <stdio.h>

int main( void )
{
  printf("clang-format is shit\n");
  getchar();
}

int * function( int a, int b )
{
  printf("clang-format is shit\n");
  int c = a + b;
  return &c;
}