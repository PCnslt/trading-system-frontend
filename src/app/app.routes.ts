import { Routes } from '@angular/router';
import { DashboardHomeComponent } from './components/dashboard-home/dashboard-home.component';
import { ChartsPageComponent } from './components/charts-page/charts-page.component';
import { PortfolioPageComponent } from './components/portfolio-page/portfolio-page.component';

export const routes: Routes = [
  { path: '', component: DashboardHomeComponent, pathMatch: 'full' },
  { path: 'charts', component: ChartsPageComponent },
  { path: 'portfolio', component: PortfolioPageComponent },
  { path: '**', redirectTo: '' }
];