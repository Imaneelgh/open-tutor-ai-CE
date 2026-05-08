<script lang="ts">
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';
  import { onMount, getContext } from 'svelte';

  const i18n = getContext('i18n');

  // État global
  let quizzes: any[] = [];
  let activeQuiz: any = null;
  let loading = true;
  let error: string | null = null;

  // État du quiz en cours
  let currentQuestionIndex = 0;
  let selectedAnswer: number | null = null;
  let isAnswered = false;
  let score = 0;
  let quizFinished = false;

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  onMount(async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 100));
      if (!$user) { await goto('/auth'); return; }
      if ($user.role !== 'user') { await goto(`/${$user.role}`); return; }
      await fetchQuizzes();
    } catch (err: any) {
      error = err.message || "Une erreur est survenue";
    } finally {
      loading = false;
    }
  });

  async function fetchQuizzes() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/quizzes`, {
        headers: { 'Authorization': `Bearer ${$user?.token}` }
      });
      if (!response.ok) throw new Error('Échec du chargement');
      quizzes = await response.json();
    } catch (err) {
      console.warn("️ Fallback sur données de démonstration");
      // ✅ CORRECTION : correct_answer est maintenant un nombre pour éviter les bugs de type
         // Données mock - Quiz Algorithmique (10 questions)
      quizzes = [
        {
          id: 'quiz_algo_fondamentale',
          title: 'Quiz Algorithmique Fondamentale',
          description: 'Testez vos connaissances sur les structures de données, la complexité et les algorithmes classiques.',
          subject: 'Algorithmique',
          questions: [
            { id: 'q1', text: 'Qu\'est-ce qu\'un algorithme ?', question_type: 'multiple_choice', options: ['Un langage de programmation', 'Une suite finie et ordonnée d\'instructions pour résoudre un problème', 'Un type de base de données', 'Un système d\'exploitation'], correct_answer: 1, points: 1, explanation: 'Un algorithme est une séquence logique et finie d\'étapes permettant de résoudre un problème ou d\'effectuer un calcul.' },
            { id: 'q2', text: 'Quelle notation décrit la complexité temporelle dans le pire des cas ?', question_type: 'multiple_choice', options: ['Notation Omega (Ω)', 'Notation Theta (Θ)', 'Notation Big O (O)', 'Notation Sigma (Σ)'], correct_answer: 2, points: 1, explanation: 'La notation Big O (O) décrit la borne supérieure de la complexité, c\'est-à-dire le scénario le plus défavorable.' },
            { id: 'q3', text: 'Quelle structure de données fonctionne selon le principe LIFO ?', question_type: 'multiple_choice', options: ['File (Queue)', 'Tableau (Array)', 'Pile (Stack)', 'Liste chaînée'], correct_answer: 2, points: 1, explanation: 'La Pile (Stack) suit le principe LIFO : le dernier élément ajouté est le premier à être retiré.' },
            { id: 'q4', text: 'Quelle est la complexité moyenne du tri rapide (QuickSort) ?', question_type: 'multiple_choice', options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], correct_answer: 1, points: 1, explanation: 'QuickSort a une complexité moyenne de O(n log n), bien qu\'il puisse atteindre O(n²) dans le pire des cas.' },
            { id: 'q5', text: 'Dans quel cas la recherche dichotomique est-elle applicable ?', question_type: 'multiple_choice', options: ['Sur un tableau trié', 'Sur un tableau non trié', 'Sur une liste chaînée uniquement', 'Sur n\'importe quelle structure'], correct_answer: 0, points: 1, explanation: 'La recherche dichotomique nécessite que les données soient préalablement triées pour fonctionner en O(log n).' },
            { id: 'q6', text: 'Qu\'est-ce qu\'une fonction récursive ?', question_type: 'multiple_choice', options: ['Une fonction qui s\'appelle elle-même', 'Une fonction qui retourne toujours 0', 'Une fonction sans paramètres', 'Une fonction appelée uniquement depuis le main'], correct_answer: 0, points: 1, explanation: 'La récursivité est une technique où une fonction s\'appelle elle-même pour résoudre des sous-problèmes plus petits.' },
            { id: 'q7', text: 'Quel algorithme trouve le plus court chemin dans un graphe sans arêtes négatives ?', question_type: 'multiple_choice', options: ['Algorithme de Kruskal', 'Algorithme de Dijkstra', 'Algorithme de Prim', 'Parcours en profondeur (DFS)'], correct_answer: 1, points: 1, explanation: 'L\'algorithme de Dijkstra est spécialisé dans la recherche du plus court chemin à partir d\'une source unique.' },
            { id: 'q8', text: 'Quel est le principe fondamental de la programmation dynamique ?', question_type: 'multiple_choice', options: ['Utiliser uniquement des boucles', 'Stocker les résultats intermédiaires pour éviter les recalculs', 'Diviser pour régner sans mémoïsation', 'Utiliser des pointeurs uniquement'], correct_answer: 1, points: 1, explanation: 'La programmation dynamique optimise les solutions en mémorisant les résultats des sous-problèmes déjà résolus.' },
            { id: 'q9', text: 'Quelle est la complexité spatiale d\'un algorithme utilisant un tableau auxiliaire de taille n ?', question_type: 'multiple_choice', options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], correct_answer: 2, points: 1, explanation: 'Utiliser un tableau de taille n implique une consommation mémoire linéaire, notée O(n).' },
            { id: 'q10', text: 'Que mesure la complexité algorithmique ?', question_type: 'multiple_choice', options: ['Le nombre de lignes de code', 'La quantité de ressources (temps/mémoire) nécessaires à l\'exécution', 'Le nombre de fonctions utilisées', 'La difficulté de lecture du code'], correct_answer: 1, points: 1, explanation: 'La complexité algorithmique évalue l\'efficacité d\'un algorithme en termes de temps d\'exécution et d\'espace mémoire requis.' }
          ],
          time_limit_minutes: 15,
          is_active: true
        }
      ];
    }
  }

  function startQuiz(quiz: any) {
    activeQuiz = { ...quiz };
    currentQuestionIndex = 0;
    selectedAnswer = null;
    isAnswered = false;
    score = 0;
    quizFinished = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function backToList() {
    activeQuiz = null;
    fetchQuizzes();
  }

  function selectAnswer(index: number) {
    if (!isAnswered) selectedAnswer = index;
  }

  function validateAnswer() {
    if (selectedAnswer === null || isAnswered) return;
    isAnswered = true;
    const q = activeQuiz.questions[currentQuestionIndex];
    // ✅ Comparaison explicite en nombres
    if (Number(selectedAnswer) === Number(q.correct_answer)) {
      score++;
    }
  }

  function nextQuestion() {
    if (currentQuestionIndex < activeQuiz.questions.length - 1) {
      currentQuestionIndex++;
      selectedAnswer = null;
      isAnswered = false;
    } else {
      quizFinished = true;
    }
  }

  function restartQuiz() {
    activeQuiz = null;
    fetchQuizzes();
  }
</script>



{#if error}
  <div style="margin:4rem 2rem; padding:1.5rem; background:#fef2f2; border:1px solid #fecaca; border-radius:8px; text-align:center;">
    <p style="color:#991b1b; margin:0 0 1rem 0; font-weight:500;">⚠️ {error}</p>
    <button on:click={fetchQuizzes} style="padding:0.6rem 1.2rem; background:#ef4444; color:white; border:none; border-radius:6px; cursor:pointer;">Réessayer</button>
  </div>

{:else if activeQuiz}
  <div style="padding:4rem 2rem 2rem; max-width:800px; margin:0 auto;">
    <button on:click={backToList} style="margin-bottom:1.5rem; color:#3b82f6; background:none; border:none; cursor:pointer; font-weight:500;">← Retour à la liste</button>

    {#if quizFinished}
      <div style="background:#fff; padding:2.5rem; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); text-align:center;">
        <h2 style="margin:0 0 1rem 0; font-size:1.8rem;">🎉 Quiz Terminé !</h2>
        <div style="font-size:3rem; font-weight:bold; color:#3b82f6; margin:1rem 0;">{score} / {activeQuiz.questions.length}</div>
        <p style="color:#6b7280; margin-bottom:2rem;">
          {score === activeQuiz.questions.length ? 'Parfait ! 🌟' : score >= activeQuiz.questions.length / 2 ? 'Bon travail ! ' : 'Continuez à pratiquer ! '}
        </p>
        <button on:click={restartQuiz} style="padding:0.8rem 1.5rem; background:#3b82f6; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600;">
          Retour aux quiz
        </button>
      </div>
    {:else}
      {@const q = activeQuiz.questions[currentQuestionIndex]}
      <div style="background:#fff; padding:2rem; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid #e5e7eb;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #e5e7eb;">
          <h3 style="margin:0; font-size:1.1rem; color:#6b7280; font-weight:500;">Question {currentQuestionIndex + 1} sur {activeQuiz.questions.length}</h3>
          {#if activeQuiz.time_limit_minutes}
            <span style="background:#dbeafe; color:#1e40af; padding:0.3rem 0.8rem; border-radius:9999px; font-size:0.85rem;">⏱️ {activeQuiz.time_limit_minutes} min</span>
          {/if}
        </div>

        <p style="font-size:1.25rem; font-weight:600; color:#111827; margin:0 0 1.5rem 0;">{q.text}</p>

        <div style="display:flex; flex-direction:column; gap:0.75rem; margin-bottom:2rem;">
          {#each q.options as option, index}
            {@const isCorrect = Number(index) === Number(q.correct_answer)}
            {@const isSelected = selectedAnswer === index}
            <label style="display:flex; align-items:center; padding:1rem; border:2px solid {isAnswered ? (isCorrect ? '#22c55e' : (isSelected ? '#ef4444' : '#e5e7eb')) : (isSelected ? '#3b82f6' : '#e5e7eb')}; border-radius:8px; cursor:{isAnswered ? 'default' : 'pointer'}; background:{isSelected ? '#f8fafc' : '#fff'}; transition:all 0.2s;">
              <input type="radio" name="q" value={index}
                on:change={() => selectAnswer(index)}
                checked={isSelected}
                disabled={isAnswered}
                style="margin-right:0.75rem; accent-color:#3b82f6; width:1.1rem; height:1.1rem;" />
              <span style="color:#374151;">{option}</span>
            </label>
          {/each}
        </div>

        {#if !isAnswered}
          <button on:click={validateAnswer} disabled={selectedAnswer === null}
            style="width:100%; padding:0.8rem; background:{selectedAnswer === null ? '#9ca3af' : '#3b82f6'}; color:white; border:none; border-radius:8px; cursor:{selectedAnswer === null ? 'not-allowed' : 'pointer'}; font-weight:600; font-size:1rem;">
             Valider la réponse
          </button>
        {:else}
          <div style="padding:1rem; background:{Number(selectedAnswer) === Number(q.correct_answer) ? '#f0fdf4' : '#fef2f2'}; border:1px solid {Number(selectedAnswer) === Number(q.correct_answer) ? '#bbf7d0' : '#fecaca'}; border-radius:8px; margin-bottom:1rem;">
            <p style="margin:0 0 0.5rem 0; font-weight:600; color:{Number(selectedAnswer) === Number(q.correct_answer) ? '#166534' : '#991b1b'};">
              {Number(selectedAnswer) === Number(q.correct_answer) ? '✅ Bonne réponse !' : '❌ Mauvaise réponse.'}
            </p>
            {#if q.explanation}
              <p style="margin:0; color:#4b5563; font-size:0.95rem;">💡 {q.explanation}</p>
            {/if}
          </div>

          <button on:click={nextQuestion}
            style="width:100%; padding:0.8rem; background:#3b82f6; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600; font-size:1rem;">
            {currentQuestionIndex === activeQuiz.questions.length - 1 ? '🏆 Voir les résultats' : 'Question suivante →'}
          </button>
        {/if}
      </div>
    {/if}
  </div>

{:else}
  <div style="padding:4rem 2rem 2rem; max-width:1200px; margin:0 auto;">
    <header style="margin-bottom:2rem;">
      <button on:click={() => goto('/student/dashboard')} style="margin-bottom:1rem; color:#3b82f6; background:none; border:none; cursor:pointer; font-weight:500;">← Retour au Dashboard</button>
      <h1 style="font-size:2rem; margin:0; color:#111827;">📝 Mes Quiz</h1>
      <p style="color:#6b7280; margin:0.5rem 0 0 0;">Testez vos connaissances et progressez à votre rythme !</p>
    </header>

    {#if quizzes.length === 0}
      <div style="text-align:center; padding:4rem 2rem; background:#f9fafb; border-radius:12px; border:2px dashed #e5e7eb;">
        <p style="font-size:1.25rem; margin:0 0 1rem 0; color:#374151; font-weight:500;">🎯 Aucun quiz disponible pour le moment.</p>
      </div>
    {:else}
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:1.5rem;">
        {#each quizzes as quiz}
          <div style="border:1px solid #e5e7eb; border-radius:12px; padding:1.5rem; background:#fff;">
            <h3 style="margin:0 0 0.5rem 0; font-size:1.25rem; color:#111827;">{quiz.title}</h3>
            <p style="color:#3b82f6; margin:0 0 0.5rem 0; font-weight:600; font-size:0.9rem; text-transform:uppercase;">{quiz.subject}</p>
            <p style="color:#6b7280; margin:0 0 1rem 0; font-size:0.9rem;">{quiz.description}</p>
            <div style="display:flex; gap:1rem; margin-bottom:1rem; font-size:0.85rem; color:#6b7280;">
              <span>📝 {quiz.questions?.length || 0} questions</span>
              {#if quiz.time_limit_minutes}<span>⏱️ {quiz.time_limit_minutes} min</span>{/if}
            </div>
            <button on:click={() => startQuiz(quiz)} disabled={!quiz.is_active}
              style="width:100%; padding:0.75rem; background:{quiz.is_active ? '#3b82f6' : '#9ca3af'}; color:white; border:none; border-radius:8px; cursor:{quiz.is_active ? 'pointer' : 'not-allowed'}; font-weight:600;">
              {quiz.is_active ? 'Commencer le Quiz' : 'Indisponible'}
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}
