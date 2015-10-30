#include "mp.h"

extern boolean OpenInner, NonReflecting, OuterSourceMass;

real GasTotalMass1D (array)
PolarGrid1D *array;
{
   int i;
   real *density, total = 0.0, fulltotal=0.0;
   density = array->Field;
   if (FakeSequential && (CPU_Rank > 0)) 
     MPI_Recv (&total, 1, MPI_DOUBLE, CPU_Rank-1, 0, MPI_COMM_WORLD, &stat);
   /*   for (i = Zero_or_active; i < Max_or_active; i++) {*/
   for (i = 0; i < NRAD1D; i++) {
     total += Surf1D[i]*density[i];
   }
   if (FakeSequential) {
     if (CPU_Rank < CPU_Number-1)
       MPI_Send (&total, 1, MPI_DOUBLE, CPU_Rank+1, 0, MPI_COMM_WORLD);
   }
   else
     MPI_Allreduce (&total, &fulltotal, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
   if (FakeSequential) {
     MPI_Bcast (&total, 1, MPI_DOUBLE, CPU_Number-1, MPI_COMM_WORLD);
     fulltotal = total;
   }
   return fulltotal;
}

real GasMomentum1D (Density, Vtheta)
PolarGrid1D *Density, *Vtheta;
{
   int i;
   real *density, *vtheta, total = 0.0, fulltotal=0.0;
   density = Density->Field;
   vtheta = Vtheta->Field;
   if (FakeSequential && (CPU_Rank > 0)) 
     MPI_Recv (&total, 1, MPI_DOUBLE, CPU_Rank-1, 2, MPI_COMM_WORLD, &stat);
   /*   for (i = Zero_or_active; i < Max_or_active; i++) {*/
   for (i = 0; i < NRAD1D; i++) {
     total += Surf1D[i]*density[i]*Rmed1D[i]*(vtheta[i]+OmegaFrame*Rmed1D[i]);
   }
   if (FakeSequential) {
     if (CPU_Rank < CPU_Number-1)
       MPI_Send (&total, 1, MPI_DOUBLE, CPU_Rank+1, 2, MPI_COMM_WORLD);
   }
   else
     MPI_Allreduce (&total, &fulltotal, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
   if (FakeSequential) {
     MPI_Bcast (&total, 1, MPI_DOUBLE, CPU_Number-1, MPI_COMM_WORLD);
     fulltotal = total;
   }
   return fulltotal;
}

void DivisePolarGrid1D (Num, Denom, Res)
PolarGrid1D *Num, *Denom, *Res;
{
  int i,nr;
  real *num, *denom, *res;
  num = Num->Field;
  denom=Denom->Field;
  res = Res->Field;
  nr = Res->Nrad;
  for (i = 0; i <= nr; i++) {
    res[i] = num[i]/(denom[i]+1e-20);
  }
}


void OpenBoundary1D (Vrad, Rho)
PolarGrid1D *Vrad, *Rho;
{
  int i;
  real *rho, *vr;
  if (!(IAmTheFirst || IAmTheLast)) return;
  rho = Rho->Field;
  vr  = Vrad->Field;
  /* INNER EDGE */
  i = 1;
  rho[i-1] = rho[i];
  if ((vr[2] > 0.0)) /* No condition on the density to enable
			the disk to accrete onto the central star.*/
    vr[i] = 0.0;
  else
    vr[i] = vr[i+1];
  /* OUTER EDGE : */
  i = NRAD1D-1;
  rho[i] = rho[i-1];
  if ((vr[i-1] < 0.0)) /* No condition on the density to enable
			  the disk to spread outwards.*/
    vr[i] = 0.0;
  else
    vr[i] = vr[i-1];
  vr[NRAD1D]=0.;
}

void FixedMdotBoundary1D (Vrad, Rho)
PolarGrid1D *Vrad, *Rho;
{
/* Fix outer boundaries to satisfy a constant Mdot accretion disk.
   Keep inner boundary condition to outflow.
*/
  int i;
  real *rho, *vr;
  real nu;
  if (!(IAmTheFirst || IAmTheLast)) return;
  rho = Rho->Field;
  vr  = Vrad->Field;
  /* INNER EDGE */
  i = 1;
  rho[i-1] = rho[i];
  if ((vr[2] > 0.0)) /* No condition on the density to enable
			the disk to accrete onto the central star.*/
    vr[i] = 0.0;
  else
    vr[i] = vr[i+1];
  /* OUTER EDGE : */
  i = NRAD1D-1;
  nu = ALPHAVISCOSITY * ASPECTRATIO *ASPECTRATIO * pow(Rmed1D[i],0.5 + 2*FLARINGINDEX);
  rho[i] = MDOT /(3*M_PI*nu);
 // rho[i] = rho[i-1];
  vr[i] = -1.5*nu/Rmed1D[i];

  nu =  ALPHAVISCOSITY * ASPECTRATIO *ASPECTRATIO * pow(RMAX1D,0.5 + 2*FLARINGINDEX);
  vr[NRAD1D] = 0;//-1.5*nu/RMAX1D;

}

void AlphaDiskBoundary1D (Vrad, Rho)
PolarGrid1D *Vrad, *Rho;
{
/* Fix outer boundaries to satisfy a constant Mdot accretion disk.
   Keep inner boundary condition to outflow.
*/
  int i;
  real *rho, *vr;
  real nu;
  if (!(IAmTheFirst || IAmTheLast)) return;
  rho = Rho->Field;
  vr  = Vrad->Field;
  /* INNER EDGE */
  i = 1;
//  rho[i-1] = rho[i];
  rho[0] = rho[1] * pow(Rmed1D[0]/Rmed1D[1],log(rho[1]/rho[2])/log(Rmed1D[1]/Rmed1D[2]));

  nu = ALPHAVISCOSITY * ASPECTRATIO * ASPECTRATIO * pow(Rmed1D[0],0.5+2*FLARINGINDEX);

  vr[0] = -1.5*nu/Rmed1D[0];

  printf("Rho:\t%lg\t%lg\t%lg\t%lg\t%lg\t%lg\n",Rmed1D[i-1],rho[i-1],Rmed1D[i],rho[i],Rmed1D[i+1],rho[i+1]);
 
  vr[1] = vr[0] * pow(Rmed[1]/Rmed[0], -0.5 + 2*FLARINGINDEX);

  printf("Vr:\t%lg\t%lg\t%lg\t%lg\t%lg\n",Rmed1D[i-1],vr[i-1],Rmed1D[i],vr[i],Rmed1D[i+1],vr[i+1]);

  /* OUTER EDGE : */
  i = NRAD1D-1;
  nu = ALPHAVISCOSITY * ASPECTRATIO *ASPECTRATIO * pow(Rmed1D[i],0.5 + 2*FLARINGINDEX);
  rho[i] = MDOT /(3*M_PI*nu);
 // rho[i] = rho[i-1];
  vr[i] = -1.5*nu/Rmed1D[i];

  nu =  ALPHAVISCOSITY * ASPECTRATIO *ASPECTRATIO * pow(RMAX1D,0.5 + 2*FLARINGINDEX);
  vr[NRAD1D] = 0;//-1.5*nu/RMAX1D;

}


void ApplyOuterSourceMass1D (Rho, Vrad)
PolarGrid1D *Rho, *Vrad;
{
  int i,nr;
  real *rho, *vr, penul_vr;
  if (!IAmTheLast) return;
  nr = Rho->Nrad;
  rho= Rho->Field;
  vr = Vrad->Field;
  i = nr-1;
  rho[i] = SigmaMed1D[nr-1];
  i = nr-1;
  penul_vr = IMPOSEDDISKDRIFT*pow((Rinf1D[nr-1]/1.0),-SIGMASLOPE);
  vr[i] = penul_vr;
}


void ApplyBoundaryCondition1D (Vrad, Rho)
PolarGrid1D *Vrad, *Rho;
{
//  OpenBoundary1D (Vrad, Rho);
   FixedMdotBoundary1D (Vrad,Rho); 
//   AlphaDiskBoundary1D (Vrad, Rho);

 if (OuterSourceMass == YES) ApplyOuterSourceMass1D (Rho, Vrad);
}

void CorrectVtheta1D (vtheta, domega)
PolarGrid1D *vtheta;
real domega;
{
  int i,nr;
  real *vt;
  nr = vtheta->Nrad;
  vt = vtheta->Field;
  for (i = 0; i < nr; i++) {
      vt[i] -= domega*Rmed1D[i];
  }
}
