/***************************************************************
 * Copyright (C) 2023
 *    Computer Graphics Support Group of 30 Phys-Math Lyceum
 ***************************************************************/

/* FILE NAME   : ttp_res_mtl.c
 * PURPOSE     : Tough Third Planet project.
 *               Resourse handle subsystem.
 *               Materials handle module.
 * PROGRAMMER  : CGSG'2022.
 *               Artem Vysotin (AV1).
 * LAST UPDATE : 15.05.2023
 * NOTE        : Module prefix 'ttp'.
 *
 * No part of this file may be changed without agreement of
 * Computer Graphics Support Group of 30 Phys-Math Lyceum
 */

#include "ttp.h"

/* Materials stock */
static ttpSTOCK TTP_MtlStock;

/* Create material from pattern function.
 * ARGUMENTS:
 *   - material name:
 *       CHAR *Name;
 *   - material pattern:
 *       ttpMATERIAL_PATTERN *pat;
 *   - material parameters(Ka, Kd, Ks, Ph):
 *       CHAR *MtlDataStr;
 *   - material textures:
 *       CHAR *TexName;
 *   - transparency material flag:
 *       BOOL IsTransparency;
 * RETURNS:
 *   (ttpMATERIAL *) created material.
 */
static ttpMATERIAL *TTP_RndResMtlCreate(CHAR *Name, ttpMATERIAL_PATTERN *MtlPat, CHAR *MtlDataStr, CHAR *TexName, BOOL IsTransparency)
{
  static ttpPARAMS params;
  ttpMATERIAL *mtl = TTP_StockAlloc(&TTP_MtlStock);
  FLT *MtlData;
  INT i, j, k, offset;

  memset(mtl, 0, sizeof(ttpMATERIAL));
  strncpy(mtl->Name, Name, TTP_MAX_NAME - 1);
  mtl->MtlPat = MtlPat;

  if (TexName != NULL)
  {
    /* Parse texture name string */
    TTP_Parser(&params, TexName);
    /* Check number of read textures */
    if (params.NumOfArgs > MtlPat->NumOfTextures)
      params.NumOfArgs = MtlPat->NumOfTextures;
    mtl->NumOfTextures = params.NumOfArgs;
    /* Load textures */
    for (i = 0; i < mtl->NumOfTextures; i++)
      mtl->Tex[i] = Ttp->TexAttach(Ttp->TexLoad(params.Args[i].ArgsStr[0]));
  }
  mtl->IsTrans = IsTransparency;

  /* Check material attributes */
  if (MtlPat->MtlAttrsSize == 0)
    return mtl;

  /* Allocate memory for material parameters */
  MtlData = malloc(sizeof(FLT) * (MtlPat->MtlAttrsSize / 4 + TTP_MAX_MATERIAL_TEXTURES));

  /* Clear material data array */
  memset(MtlData, 0, sizeof(FLT) * (MtlPat->MtlAttrsSize / 4 + TTP_MAX_MATERIAL_TEXTURES));

  /* Write material data */
  if (MtlDataStr != NULL)
  {
    /* Parse material data string */
    TTP_Parser(&params, MtlDataStr);

    for (i = 0; i < params.NumOfArgs; i++)
      for (j = 0; j < MtlPat->MtlNumOfAttrs; j++)
      {
        if (strcmp(params.Args[i].Name, MtlPat->MtlAttrs[j].Name) == 0)
        {
          if (params.Args[i].NumOfArgs == 1)
            for (k = 0; k < MtlPat->MtlAttrs[j].Size; k++)
              MtlData[MtlPat->MtlAttrs[j].Offset / 4 + k] = params.Args[i].ArgsDbl[0];
          else
            for (k = 0; k < MtlPat->MtlAttrs[j].Size; k++)
              MtlData[MtlPat->MtlAttrs[j].Offset / 4 + k] = params.Args[i].ArgsDbl[k];
          break;
        }
      }
    /* Add textures flags */
    offset = MtlPat->MtlAttrsSize / 4;
    for (i = 0; i < TTP_MAX_MATERIAL_TEXTURES; i++)
      if (mtl->Tex[i] != NULL)
        MtlData[i + offset] = 1;
      else
        MtlData[i + offset] = 0;
  }
  mtl->UBO = Ttp->UBOCreate(mtl->Name, TTP_RND_UBO_BIND_MATERIAL, MtlPat->MtlAttrsSize + TTP_MAX_MATERIAL_TEXTURES * 4, MtlData);
  free(MtlData);
  return mtl;
} /* End of 'TTP_RndResMtlCreate' function */

/* Create material from pattern with textures function.
 * ARGUMENTS:
 *   - material name:
 *       CHAR *Name;
 *   - material pat tern:
 *       ttpMATERIAL_PATTERN *pat;
 *   - material parameters(Ka, Kd, Ks, Ph):
 *       CHAR *MtlDataStr;
 *   - material textures:
 *       ttpTEXTURE *Tex;
 *   - number of textures:
 *       INT NumOfTextures;
 *   - transparency material flag:
 *       BOOL IsTransparency;
 * RETURNS:
 *   (ttpMATERIAL *) created material.
 */
static ttpMATERIAL *TTP_RndResMtlCreateTex(CHAR *Name,  ttpMATERIAL_PATTERN *MtlPat, CHAR *MtlDataStr,  ttpTEXTURE **Tex, INT NumOfTextures, BOOL IsTransparency)
{
  static ttpPARAMS params;
  ttpMATERIAL *mtl = TTP_StockAlloc(&TTP_MtlStock);
  FLT *MtlData;
  INT i, j, k, offset;

  memset(mtl, 0, sizeof(ttpMATERIAL));
  strncpy(mtl->Name, Name, TTP_MAX_NAME - 1);
  mtl->MtlPat = MtlPat;

  /* Load textures */
  if (NumOfTextures > MtlPat->NumOfTextures)
    NumOfTextures = MtlPat->NumOfTextures;
  for (i = 0; i < NumOfTextures; i++)
    mtl->Tex[i] = Ttp->TexAttach(Tex[i]);
  mtl->NumOfTextures = NumOfTextures;

  mtl->IsTrans = IsTransparency;

  /* Allocate memory for material parameters */
  MtlData = malloc(sizeof(FLT) * (MtlPat->MtlAttrsSize / 4 + TTP_MAX_MATERIAL_TEXTURES));

  /* Clear material data array */
  memset(MtlData, 0, sizeof(FLT) * (MtlPat->MtlAttrsSize / 4 + TTP_MAX_MATERIAL_TEXTURES));

  /* Write material data */
  if (MtlDataStr != NULL)
  {
    /* Parse material data string */
    TTP_Parser(&params, MtlDataStr);

    for (i = 0; i < params.NumOfArgs; i++)
      for (j = 0; j < MtlPat->MtlNumOfAttrs; j++)
      {
        if (strcmp(params.Args[i].Name, MtlPat->MtlAttrs[j].Name) == 0)
        {
          if (params.Args[i].NumOfArgs == 1)
            for (k = 0; k < MtlPat->MtlAttrs[j].Size; k++)
              MtlData[MtlPat->MtlAttrs[j].Offset / 4 + k] = params.Args[i].ArgsDbl[0];
          else
            for (k = 0; k < MtlPat->MtlAttrs[j].Size; k++)
              MtlData[MtlPat->MtlAttrs[j].Offset / 4 + k] = params.Args[i].ArgsDbl[k];
          break;
        }
      }
    /* Add textures flags */
    offset = MtlPat->MtlAttrsSize / 4;
    for (i = 0; i < TTP_MAX_MATERIAL_TEXTURES; i++)
      if (mtl->Tex[i] != NULL)
        MtlData[i + offset] = 1;
      else
        MtlData[i + offset] = 0;
  }
  mtl->UBO = Ttp->UBOCreate(mtl->Name, TTP_RND_UBO_BIND_MATERIAL, MtlPat->MtlAttrsSize + TTP_MAX_MATERIAL_TEXTURES * 4, MtlData);
  free(MtlData);
  return mtl;
} /* End of 'TTP_RndResMtlCreateTex' function */

/* Material find by name strategy function.
 * ARGUMENTS:
 *   - material:
 *       ttpMATERIAL *Mtl;
 *   - name:
 *       CHAR *Name;
 * RETURNS:
 *   (BOOL) TRUE if names identity (FALSE otherwise).
 */
static BOOL TTP_MtlFindByNameStrategy(ttpMATERIAL *Mtl, CHAR *Name)
{
  return strcmp(Mtl->Name, Name) == 0;
} /* End of 'TTP_MaterialAccessFindByName' function */

/* Get material by name function.
 * ARGUMENTS:
 *   - material name:
 *       CHAR *Name;
 * RETURNS:
 *   (ttpMATERIAL *) material.
 */
static ttpMATERIAL *TTP_RndResMtlGetByName(CHAR *Name)
{
  return TTP_StockWalkParams(&TTP_MtlStock, TTP_MtlFindByNameStrategy, Name);
} /* End of 'TTP_RndResMtlGetByName' function */

/* Delete material strategy function.
 * ARGUMENTS: 
 *   - material to delete:
 *       ttpMATERIAL *Mtl;
 * RETURNS: None.
 */
static VOID TTP_RndResMtlDeleteStrategy(ttpMATERIAL *Mtl)
{
  INT i;

  if (Mtl == NULL)
    return;

  Ttp->UBOFree(Mtl->UBO);

  for (i = 0; i < Mtl->NumOfTextures; i++)
    Ttp->TexFree(Mtl->Tex[i]);
  Mtl->UBO = NULL;
  Mtl->NumOfTextures = 0;
} /* End of 'TTP_RndResMtlDeleteStrategy' function */

/* Material free function.
 * ARGUMENTS:
 *   - material:
 *       ttpMATERIAL *Mtl;
 * RETURNS: None.
 */
static VOID TTP_RndResMtlFree(ttpMATERIAL *Mtl)
{
  if (Mtl == NULL)
    return;
  
  TTP_StockDel(Mtl);
} /* End of 'TTP_RndResMtlFree' function */

/* Apply material by material stock pointer function.
 * ARGUMENTS:
 *   - pointer to material:
 *       ttpMATERIAL *Mtl;
 * RETURNS: None.
 */
static VOID TTP_RndResMtlApply(ttpMATERIAL *Mtl)
{
  INT prg = 0, i;

  /* Set shader program Id */
  assert(Mtl != NULL);
  assert(Mtl->MtlPat != NULL);
  if (Mtl == NULL || Mtl->MtlPat == NULL || Mtl->MtlPat->Shaders[Ttp->RenderPass] == NULL)
    return;
  prg = Mtl->MtlPat->Shaders[Ttp->RenderPass]->GLProgId;
  glUseProgram(prg);

  /* Set shading parameters */
  if (Mtl->UBO != NULL)
    Ttp->UBOApply(Mtl->UBO);

  /* Set textures */
  for (i = 0; i < Mtl->NumOfTextures; i++)
    Ttp->TexActivate(Mtl->Tex[i], i);
} /* End of 'TTP_RndResMtlApply' function */

/* Materials stock initialization function.
 * ARGUMENTS: None.
 * RETURNS: None.
 */
VOID TTP_RndResMtlInit(VOID)
{
  /* Create materials stock */
  TTP_StockCreate(&TTP_MtlStock, "Materials stock", sizeof(ttpMATERIAL), 200, TTP_RndResMtlDeleteStrategy);

  Ttp->MtlCreate = TTP_RndResMtlCreate;
  Ttp->MtlGetByName = TTP_RndResMtlGetByName;
  Ttp->MtlApply = TTP_RndResMtlApply;
  Ttp->MtlCreateTex = TTP_RndResMtlCreateTex;
  Ttp->MtlFree = TTP_RndResMtlFree;
  TTP_StockAdd(&Ttp->FreezeStocks, TTP_PTR2REF(&TTP_MtlStock));
} /* End of 'TTP_RndResMtlInit' function */

/* Materials stock deinitialization function.
 * ARGUMENTS: None.
 * RETURNS: None.
 */
VOID TTP_RndResMtlClose(VOID)
{
  /* Delete materials stock */
  TTP_StockClear(&TTP_MtlStock);
  TTP_StockFree(&TTP_MtlStock);
} /* End of 'TTP_RndResMtlClose' function */

/* END OF 'ttp_res_mtl.c' FILE */
