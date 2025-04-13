/*** FLOOD FILL ***/
/* Maximum pixels store */
#define MAX_STORE 3000000

/* Store pixel list data type */
typedef struct tagPLIST PLIST;

struct tagPLIST
{
  /* Pixel coordinates */
  INT X[MAX_STORE], Y[MAX_STORE];
  PLIST *Next; /* Pointer to next element */
};

/* Point list */
static PLIST *PixelList;
static INT StoreSize;

/* Store pixel function */
VOID Store(INT X, INT Y)
{
  /* Check for free space */
  if (PixelList == NULL || StoreSize >= MAX_STORE)
  {
    /* Add new block */
    PLIST *NewElement = malloc(sizeof(PLIST));

    if (NewElement == NULL)
      return;
    NewElement->Next = PixelList;
    PixelList = NewElement;
    StoreSize = 0;
  }
  PixelList->X[StoreSize] = X;
  PixelList->Y[StoreSize] = Y;
  StoreSize++;
} /* End of 'Store' function */

/* Store pixel function */
BOOL Restore(INT *X, INT *Y)
{
  if (PixelList == NULL || StoreSize == 0)
    return FALSE;
  StoreSize--;
  *X = PixelList->X[StoreSize];
  *Y = PixelList->Y[StoreSize];
  if (StoreSize == 0)
  {
    PLIST *OldElement;

    /* Free empty block */
    OldElement = PixelList;
    PixelList = PixelList->Next;
    free(OldElement);
    if (PixelList != NULL)
      StoreSize = MAX_STORE;
  }
  return TRUE;
} /* End of 'Store' function */

DWORD GFX_GetPixel(INT X, INT Y)
{
  return GFX_Frame[X * Y];
}

VOID GFX_FloodFill(INT X, INT Y, DWORD Color)
{
  DWORD BlackColor = GFX_GetPixel(X, Y);

  if (BlackColor == Color)
    return;

  Store(X, Y);
  while (Restore(&X, &Y))
    if (X >= 0 && Y >= 0 && X <= GFX_FRAME_W && Y <= GFX_FRAME_H &&
        GFX_GetPixel(X, Y) == BlackColor)
    {
      GFX_PutPixel(X, Y, Color);
      Store(X - 1, Y);
      Store(X + 1, Y);
      Store(X, Y - 1);
      Store(X, Y + 1);
    }
}
