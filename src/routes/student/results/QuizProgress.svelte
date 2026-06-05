<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  let quizzes: any[] = [];
  let loading = true;

  // Au chargement du composant, on récupère les quiz
  onMount(async () => {
    await fetchQuizzes();
    loading = false;
  });

  async function fetchQuizzes() {
    try {
      // 1. On essaie de récupérer les vrais quiz depuis ton backend Python
      const response = await fetch(`${API_BASE}/api/v1/quizzes`, {
        headers: { 'Authorization': `Bearer ${$user?.token}` }
      });
      if (!response.ok) throw new Error('Échec du chargement');
      quizzes = await response.json();
    } catch (err) {
      // 2. Si le backend ne répond pas, on utilise les mêmes données de secours que ta page Quizzes
      console.warn("⚠️ Fallback sur données de démonstration");
      quizzes = [
        {
          id: 'quiz_algo_fondamentale',
          title: 'Quiz Algorithmique Fondamentale',
          description: 'Testez vos connaissances sur les structures de données...',
          subject: 'Algorithmique',
          questions: Array(10).fill({}), // Simplifié pour l'exemple, l'important est l'ID
          time_limit_minutes: 7,
          is_active: true
        },
        {
          id: 'quiz_structures_donnees',
          title: 'Quiz Structures de Données',
          description: 'Maîtrisez les tableaux, listes, piles, files...',
          subject: 'Algorithmique',
          questions: Array(10).fill({}),
          time_limit_minutes: 7,
          is_active: true
        }
      ];
    }
    
    // 3. Une fois les quiz chargés, on calcule leur statut (Terminé, Disponible, Verrouillé)
    calculateProgress();
  }

  function calculateProgress() {
    // 🪄 LA MAGIE : On va lire ce que ta page Quizzes a sauvegardé dans le navigateur !
    const savedResults = JSON.parse(localStorage.getItem('quiz_results') || '[]');
    
    // On crée un dictionnaire pour retrouver vite les scores des quiz terminés
    const completedData = new Map();
    savedResults.forEach((result: any) => {
      // On garde le score le plus récent pour chaque quiz
      if (!completedData.has(result.quizId)) {
        completedData.set(result.quizId, result.percentage);
      }
    });

    // On parcourt les quiz pour définir leur statut
    quizzes = quizzes.map((quiz, index) => {
      let status = 'locked'; // Par défaut, tout est verrouillé
      let score = null;

      // Cas 1 : Le quiz est dans le localStorage, donc il est terminé
      if (completedData.has(quiz.id)) {
        status = 'completed';
        score = completedData.get(quiz.id) + '%';
      } 
      // Cas 2 : Le quiz n'est pas terminé, MAIS c'est le premier OU le précédent est terminé
      else if (index === 0 || completedData.has(quizzes[index - 1].id)) {
        status = 'available';
      }

      // On retourne le quiz avec son nouveau statut et son score
      return { ...quiz, status, score };
    });
  }

  function handleAction(quiz: any) {
    if (quiz.status === 'available') {
      // Si le quiz est disponible, on redirige vers la page des Quiz pour le lancer
      goto('/student/quizzes'); 
    } else if (quiz.status === 'completed') {
      // S'il est terminé, on pourrait le rediriger pour revoir les réponses (pour l'instant on fait pareil)
      goto('/student/quizzes');
    }
  }
</script>

<!-- === L'AFFICHAGE HTML === -->
<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mt-8">
  
  <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
    📚 Ma Progression des Quiz
  </h3>

  {#if loading}
    <p class="text-center text-gray-500 py-4">Chargement de la progression...</p>
  {:else}
    <div class="space-y-4">
      {#each quizzes as quiz}
        
        <!-- Le design change selon le statut -->
        <div class="flex items-center justify-between p-4 rounded-lg border transition-colors
                    {quiz.status === 'locked' ? 'bg-gray-100 border-gray-200 opacity-60' : 'bg-white border-gray-200 hover:border-blue-400'}">
          
          <div class="flex items-center gap-4">
            <!-- Icône dynamique -->
            {#if quiz.status === 'completed'}
              <span class="text-2xl">✅</span>
            {:else if quiz.status === 'available'}
              <span class="text-2xl">▶️</span>
            {:else}
              <span class="text-2xl">🔒</span>
            {/if}

            <div>
              <p class="font-semibold text-gray-800">{quiz.title}</p>
              
              <!-- Texte dynamique -->
              {#if quiz.status === 'completed'}
                <p class="text-sm text-green-600 font-bold">Terminé - Score: {quiz.score}</p>
              {:else if quiz.status === 'available'}
                <p class="text-sm text-blue-600">Disponible à passer</p>
              {:else}
                <p class="text-sm text-gray-500">Verrouillé (Termine le précédent)</p>
              {/if}
            </div>
          </div>

          <!-- Bouton d'action -->
          <button 
            class="px-4 py-2 rounded-lg text-sm font-bold transition-colors
                   {quiz.status === 'locked' ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}"
            disabled={quiz.status === 'locked'}
            on:click={() => handleAction(quiz)}
          >
            {quiz.status === 'completed' ? 'Revoir' : (quiz.status === 'available' ? 'Commencer' : 'Verrouillé')}
          </button>
        </div>

      {/each}
    </div>
  {/if}
</div>