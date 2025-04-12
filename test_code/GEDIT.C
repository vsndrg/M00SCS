/* ED2, 23.12.2022 */
#include <windows.h>
#include "gedit.h"
#include "glut.h"

VOID GFX_PutLine( INT X1, INT Y1, INT X2, INT Y2, DWORD Color )
{
  INT X, Y, IncrE, IncrNE, F, dx, dy, sx, count, tmp;

  if (Y2 < Y1)
    tmp = X1, X1 = X2, X2 = tmp, tmp = Y1, Y1 = Y2, Y2 = tmp;
  dy = Y2 - Y1;
  if ((dx = X2 - X1) < 0)
    dx = -dx, sx = -1;
  else
    sx = 1;

  X = X1;
  Y = Y1;
  GFX_PutPixel(X, Y, Color);
  if (dx >= dy)
  {
    F = 2 * dy - dx;
    IncrE = 2 * dy;
    IncrNE = 2 * dy - 2 * dx;
    count = dx;
    while (count-- > 0)
    {
      if (F > 0)
        Y++, F += IncrNE;
      else
        F += IncrE;
      X += sx;
      GFX_PutPixel(X, Y, Color);
    }
  }
  else
  {
    F = 2 * dx - dy;
    IncrE = 2 * dx;
    IncrNE = 2 * dx - 2 * dy;
    count = dy;
    while (count-- > 0)
    {
      if (F > 0)
        X += sx, F += IncrNE;
      else
        F += IncrE;
      Y++;
      GFX_PutPixel(X, Y, Color);
    }
  }
}

static VOID GFX_Put4Points( INT X, INT Y, INT Xc, INT Yc, DWORD Color )
{
  GFX_PutPixel(Xc + X, Yc + Y, Color);
  GFX_PutPixel(Xc + X, Yc - Y, Color);
  GFX_PutPixel(Xc + Y, Yc + X, Color);
  GFX_PutPixel(Xc - Y, Yc + X, Color);
}

static VOID GFX_Put8Points( INT X, INT Y, INT Xc, INT Yc, DWORD Color )
{
  GFX_PutPixel(Xc + X, Yc + Y, Color);
  GFX_PutPixel(Xc + Y, Yc + X, Color);
  GFX_PutPixel(Xc + Y, Yc - X, Color);
  GFX_PutPixel(Xc + X, Yc - Y, Color);
  GFX_PutPixel(Xc - X, Yc - Y, Color);
  GFX_PutPixel(Xc - Y, Yc - X, Color);
  GFX_PutPixel(Xc - Y, Yc + X, Color);
  GFX_PutPixel(Xc - X, Yc + Y, Color);
}

VOID GFX_PutCircle( INT Xc, INT Yc, INT R, DWORD Color )
{
  INT F, IncrE, IncrSE, X, Y;

  F = 1 - R;
  IncrE = 3;
  IncrSE = 5 - 2 * R;
  X = 0;
  Y = R;
  GFX_Put4Points(X, Y, Xc, Yc, Color);
  while (1)
  {
    if (F >= 0)
      Y--, F += IncrSE, IncrSE += 4;
    else
      F += IncrE, IncrSE += 2;
    IncrE += 2;
    X++;
    if (X > Y)
      break;
    GFX_Put8Points(X, Y, Xc, Yc, Color);
  }
}

VOID DrawRose( INT Xc, INT Yc, INT L, INT Sh, DWORD ColorLight, DWORD ColorDark )
{
  INT i;

  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc - i, Yc - i, Xc - i, Yc - L + i * (L - Sh) / Sh, ColorLight);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc + i, Yc - i, Xc + L - i * (L - Sh) / Sh, Yc - i, ColorLight);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc + i, Yc + i, Xc + i, Yc + L - i * (L - Sh) / Sh, ColorLight);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc - i, Yc + i, Xc - L + i * (L - Sh) / Sh, Yc + i, ColorLight);

  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc + i, Yc - i, Xc + i, Yc - L + i * (L - Sh) / Sh, ColorDark);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc + i, Yc + i, Xc + L - i * (L - Sh) / Sh, Yc + i, ColorDark);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc - i, Yc + i, Xc - i, Yc + L - i * (L - Sh) / Sh, ColorDark);
  for (i = 0; i < Sh; i++)
    GFX_PutLine(Xc - i, Yc - i, Xc - L + i * (L - Sh) / Sh, Yc - i, ColorDark);
}


typedef struct tagLIST LIST;
struct tagLIST
{
  INT X, Y;
  LIST *Next;
} *Stock;

VOID GFX_Store( INT X, INT Y )
{
  LIST *NE;

  if ((NE = malloc(sizeof(LIST))) == NULL)
    return;
  NE->X = X;
  NE->Y = Y;
  NE->Next = Stock;
  Stock = NE;
}

BOOL GFX_Restore( INT *X, INT *Y )
{
  LIST *Old;

  if (Stock == NULL)
    return FALSE;
  *X = Stock->X;
  *Y = Stock->Y;
  Old = Stock;
  Stock = Stock->Next;
  free(Old);
  return TRUE;
}

DWORD GFX_GetPixel( INT X, INT Y )
{
  return GFX_Frame[X * Y];
}

VOID GFX_FloodFill( INT X, INT Y, DWORD Color )
{
  DWORD BlackColor = GFX_GetPixel(X, Y);

  if (BlackColor == Color)
    return;

  GFX_Store(X, Y);
  while (GFX_Restore(&X, &Y))
    if (X >= 0 && Y >= 0 &&
      X <= GFX_FRAME_W && Y <= GFX_FRAME_H &&
      GFX_GetPixel(X, Y) == BlackColor)
    {
      GFX_PutPixel(X, Y, Color);
      GFX_Store(X - 1, Y);
      GFX_Store(X + 1, Y);
      GFX_Store(X, Y - 1);
      GFX_Store(X, Y + 1);
    }
}

