// contribution by nohaila Mebsat
<script lang="ts">
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';
  import { onMount } from 'svelte';

  let results: any[] = [];
  let stats = { total: 0, avgScore: 0, bestScore: 0, lastDate: '-' };
  let loading = true;

  onMount(() => {
    if (!$user) {
      goto('/auth');
      return;
    }
    loadResults();
    loading = false;
  });

  function loadResults() {
    try {
      // ✅ Clé exacte utilisée par saveQuizResult()
      const data = localStorage.getItem('quiz_results');
      
      if (!data) {
        results = [];
        calculateStats();
        return;
      }
      
      const parsed = JSON.parse(data);
      
      // ✅ Vérifie que c'est bien un tableau
      results = Array.isArray(parsed) ? parsed : [];
      
      // ✅ Trie par date décroissante (plus récent en premier)
      results.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      
      calculateStats();
    } catch (err) {
      console.error("❌ Erreur chargement résultats:", err);
      results = [];
      calculateStats();
    }
  }

  function calculateStats() {
    if (results.length === 0) {
      stats = { total: 0, avgScore: 0, bestScore: 0, lastDate: '-' };
      return;
    }
    
    stats.total = results.length;
    stats.avgScore = Math.round(results.reduce((sum, r) => sum + (r.percentage || 0), 0) / results.length);
    stats.bestScore = Math.max(...results.map((r: any) => r.percentage || 0));
    stats.lastDate = results[0]?.dateFormatted || new Date(results[0]?.date).toLocaleDateString('fr-FR');
  }

  function clearHistory() {
    if (confirm('⚠️ Voulez-vous vraiment effacer tout l\'historique des quiz ?\n\nCette action est irréversible.')) {
      localStorage.removeItem('quiz_results');
      results = [];
      stats = { total: 0, avgScore: 0, bestScore: 0, lastDate: '-' };
    }
  }

  function getScoreColor(percentage: number): string {
    if (percentage >= 80) return 'bg-green-100 text-green-800 border-green-200';
    if (percentage >= 50) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  }

  function getScoreEmoji(percentage: number): string {
    if (percentage >= 80) return '🌟';
    if (percentage >= 50) return '👍';
    return '💪';
  }

  function getSubjectBadge(subject: string): string {
    const colors: Record<string, string> = {
      'Algorithmique': 'bg-blue-100 text-blue-800',
      'Mathématiques': 'bg-purple-100 text-purple-800',
      'Programmation': 'bg-emerald-100 text-emerald-800'
    };
    return colors[subject] || 'bg-gray-100 text-gray-800';
  }
</script>

<div style="padding: 4rem 2rem 2rem; max-width: 1100px; margin: 0 auto;">
  <!-- Bouton retour -->
  <button 
    on:click={() => goto('/student/dashboard')} 
    style="margin-bottom: 1.5rem; color: #3b82f6; background: none; border: none; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 0.5rem;"
  >
    <span>←</span> Retour au Dashboard
  </button>
  
  <!-- En-tête -->
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
    <div>
      <h1 style="font-size: 2rem; margin: 0 0 0.5rem 0; color: #111827;">📊 Mes Résultats</h1>
      <p style="color: #6b7280; margin: 0;">Suivez votre progression et améliorez vos compétences</p>
    </div>
    {#if results.length > 0}
      <button 
        on:click={clearHistory} 
        style="padding: 0.5rem 1rem; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem;"
      >
        🗑️ Effacer l'historique
      </button>
    {/if}
  </div>

  {#if loading}
    <div style="text-align: center; padding: 3rem; color: #6b7280;">
      Chargement des résultats...
    </div>
  {:else}
    <!-- Cartes Statistiques -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
      <!-- Quiz passés -->
      <div style="background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid #3b82f6;">
        <div style="font-size: 2rem; font-weight: bold; color: #1e40af;">{stats.total}</div>
        <div style="color: #6b7280; font-size: 0.9rem;">Quiz Passés</div>
      </div>
      
      <!-- Score moyen -->
      <div style="background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid #10b981;">
        <div style="font-size: 2rem; font-weight: bold; color: #047857;">{stats.avgScore}%</div>
        <div style="color: #6b7280; font-size: 0.9rem;">Score Moyen</div>
      </div>
      
      <!-- Meilleur score -->
      <div style="background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid #f59e0b;">
        <div style="font-size: 2rem; font-weight: bold; color: #b45309;">{stats.bestScore}% {getScoreEmoji(stats.bestScore)}</div>
        <div style="color: #6b7280; font-size: 0.9rem;">Meilleur Score</div>
      </div>
      
      <!-- Dernière activité -->
      <div style="background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid #8b5cf6;">
        <div style="font-size: 1.2rem; font-weight: bold; color: #7c3aed;">{stats.lastDate}</div>
        <div style="color: #6b7280; font-size: 0.9rem;">Dernière Activité</div>
      </div>
    </div>

    <!-- Tableau des Résultats -->
    {#if results.length === 0}
      <div style="text-align: center; padding: 4rem 2rem; background: #f9fafb; border-radius: 12px; border: 2px dashed #e5e7eb;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
        <p style="font-size: 1.25rem; color: #6b7280; margin: 0 0 1rem 0;">Aucun résultat pour le moment.</p>
        <p style="color: #9ca3af; margin-bottom: 1.5rem;">Passez votre premier quiz pour commencer à suivre votre progression !</p>
        <button 
          on:click={() => goto('/student/quizzes')} 
          style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;"
        >
          🎯 Passer un quiz
        </button>
      </div>
    {:else}
      <div style="background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden;">
        <!-- En-tête du tableau -->
        <div style="padding: 1rem 1.5rem; background: #f9fafb; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
          <h2 style="margin: 0; font-size: 1.1rem; color: #374151; font-weight: 600;">Historique des quiz</h2>
          <span style="color: #6b7280; font-size: 0.875rem;">{results.length} résultat{results.length > 1 ? 's' : ''}</span>
        </div>
        
        <!-- Tableau -->
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: #f9fafb;">
              <tr>
                <th style="padding: 1rem; text-align: left; color: #6b7280; font-weight: 600; font-size: 0.875rem; border-bottom: 1px solid #e5e7eb;">Date</th>
                <th style="padding: 1rem; text-align: left; color: #6b7280; font-weight: 600; font-size: 0.875rem; border-bottom: 1px solid #e5e7eb;">Quiz</th>
                <th style="padding: 1rem; text-align: left; color: #6b7280; font-weight: 600; font-size: 0.875rem; border-bottom: 1px solid #e5e7eb;">Matière</th>
                <th style="padding: 1rem; text-align: center; color: #6b7280; font-weight: 600; font-size: 0.875rem; border-bottom: 1px solid #e5e7eb;">Score</th>
                <th style="padding: 1rem; text-align: center; color: #6b7280; font-weight: 600; font-size: 0.875rem; border-bottom: 1px solid #e5e7eb;">%</th>
              </tr>
            </thead>
            <tbody>
              {#each results as result}
                <tr style="border-bottom: 1px solid #f3f4f6; transition: background 0.2s;" 
                    on:mouseover={(e) => e.currentTarget.style.background = '#f9fafb'} 
                    on:mouseout={(e) => e.currentTarget.style.background = 'transparent'}>
                  <td style="padding: 1rem; color: #4b5563; font-size: 0.9rem; white-space: nowrap;">{result.dateFormatted}</td>
                  <td style="padding: 1rem; color: #111827; font-weight: 500;">{result.quizTitle}</td>
                  <td style="padding: 1rem;">
                    <span style="padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; {getSubjectBadge(result.subject)}">
                      {result.subject}
                    </span>
                  </td>
                  <td style="padding: 1rem; text-align: center; color: #4b5563; font-weight: 500;">
                    {result.score}/{result.totalQuestions}
                  </td>
                  <td style="padding: 1rem; text-align: center;">
                    <span style="padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; border: 1px solid; {getScoreColor(result.percentage)}">
                      {result.percentage}% {getScoreEmoji(result.percentage)}
                    </span>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  {/if}
</div>
