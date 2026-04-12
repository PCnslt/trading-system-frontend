import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    RouterOutlet
  ],
  template: `
    <!-- Main Content -->
    <div class="container-fluid p-0">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: []
})
export class AppComponent {
  // Navigation logic will be handled by router
}