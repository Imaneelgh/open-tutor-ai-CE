<!-- src/routes/student/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  onMount(async () => {
    await new Promise(r => setTimeout(r, 100));
    
    // 1. Vérifier l'authentification
    if (!$user) {
      await goto('/auth');
      return;
    }
    
    // 2. Vérifier le rôle
    if ($user.role !== 'user') {
      await goto(`/${$user.role}`);
      return;
    }
    
    // 3. NE REDIRIGER QUE si on est sur /student (pas /student/autre-chose)
    const currentPath = $page.url.pathname;
    
    // Seulement rediriger si on est EXACTEMENT sur /student
    if (currentPath === '/student' || currentPath === '/student/') {
      await goto('/student/dashboard');
    }
    // Sinon, laisser l'utilisateur sur la page demandée (/student/quizzes, etc.)
  });
</script>

<div class="flex items-center justify-center h-screen">
  <p>Chargement...</p>
</div>
