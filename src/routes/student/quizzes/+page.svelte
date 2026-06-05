<script lang="ts">
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';
  import { onMount, getContext } from 'svelte';
  import { afterNavigate } from '$app/navigation';
  import { onDestroy } from 'svelte';

  // Cette ligne force la page à recharger les quiz à chaque fois que tu changes de page
  afterNavigate(() => fetchQuizzes());
  const i18n = getContext('i18n');

  // === ÉTAT GLOBAL ===
  let quizzes: any[] = [];
  let activeQuiz: any = null;
  let loading = true;
  let error: string | null = null;

  // === ÉTAT DU QUIZ ===
  let currentQuestionIndex = 0;
  let selectedAnswer: number | null = null;
  let isAnswered = false;
  let score = 0;
  let quizFinished = false;
  let answers: Record<string, any> = {};
  let quizResult: any = null;

  // === ÉTAT DU TIMER AVANCÉ ===
  let timeRemaining: number | null = null;
  let totalTime: number | null = null;
  let timerInterval: any = null;
  let isTimerRunning = false;
  let isTimerPaused = false;
  
  // Flags d'alerte
  let hasWarned5min = false;
  let hasWarned2min = false;
  let hasWarned1min = false;
  
  // Audio
  let audioContext: AudioContext | null = null;

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // === CLEANUP AU DÉMONTAGE ===
  onMount(() => {
    return () => {
      if (timerInterval) clearInterval(timerInterval);
      if (audioContext) audioContext.close();
    };
  });

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
    const allQuizzes = await response.json();
    quizzes = addStatusToQuizzes(allQuizzes);
    
  } catch (err) {
    console.warn("⚠️ Fallback sur données de démonstration");
    const allQuizzes = [
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
        time_limit_minutes: 7,
        is_active: true
      },
      {
        id: 'quiz_structures_donnees',
        title: 'Quiz Structures de Données',
        description: 'Maîtrisez les tableaux, listes, piles, files, arbres et graphes : concepts, opérations et cas d\'usage.',
        subject: 'Algorithmique',
        questions: [
          { id: 's1', text: 'Quelle structure permet un accès direct à un élément par son index ?', question_type: 'multiple_choice', options: ['Liste chaînée', 'Tableau (Array)', 'Pile (Stack)', 'File (Queue)'], correct_answer: 1, points: 1, explanation: 'Les tableaux permettent un accès en O(1) via l\'index, contrairement aux listes chaînées.' },
          { id: 's2', text: 'Dans une liste chaînée simple, chaque nœud contient :', question_type: 'multiple_choice', options: ['Uniquement une valeur', 'Une valeur et un pointeur vers le nœud suivant', 'Une valeur et deux pointeurs', 'Uniquement un pointeur'], correct_answer: 1, points: 1, explanation: 'Un nœud de liste chaînée simple stocke la donnée et un pointeur vers le prochain nœud.' },
          { id: 's3', text: 'Quelle opération est O(1) sur une pile (Stack) ?', question_type: 'multiple_choice', options: ['Accès au milieu', 'Suppression du premier élément', 'Push/Pop en haut de pile', 'Recherche d\'un élément'], correct_answer: 2, points: 1, explanation: 'Push (ajout) et Pop (retrait) se font en O(1) uniquement au sommet de la pile.' },
          { id: 's4', text: 'Quelle structure suit le principe FIFO (First In, First Out) ?', question_type: 'multiple_choice', options: ['Pile (Stack)', 'File (Queue)', 'Arbre binaire', 'Table de hachage'], correct_answer: 1, points: 1, explanation: 'La File (Queue) respecte l\'ordre d\'arrivée : premier entré, premier sorti.' },
          { id: 's5', text: 'Dans un arbre binaire de recherche (BST), pour tout nœud :', question_type: 'multiple_choice', options: ['Les fils sont toujours plus grands', 'Le fils gauche < nœud < fils droit', 'Les fils sont toujours plus petits', 'Aucune règle particulière'], correct_answer: 1, points: 1, explanation: 'Le BST organise les valeurs : gauche < racine < droite, permettant une recherche efficace.' },
          { id: 's6', text: 'Quelle est la complexité d\'une recherche dans une table de hachage idéale ?', question_type: 'multiple_choice', options: ['O(n)', 'O(log n)', 'O(1)', 'O(n²)'], correct_answer: 2, points: 1, explanation: 'Avec une bonne fonction de hachage et peu de collisions, l\'accès est constant O(1).' },
          { id: 's7', text: 'Quel parcours d\'arbre visite la racine en premier ?', question_type: 'multiple_choice', options: ['In-order', 'Post-order', 'Pre-order', 'Level-order'], correct_answer: 2, points: 1, explanation: 'Le parcours Pre-order (préfixe) visite : Racine → Gauche → Droite.' },
          { id: 's8', text: 'Dans un graphe, qu\'est-ce qu\'une arête (edge) ?', question_type: 'multiple_choice', options: ['Un nœud terminal', 'Une connexion entre deux sommets', 'Un chemin cyclique', 'Une valeur pondérée'], correct_answer: 1, points: 1, explanation: 'Une arête relie deux sommets (nodes) et peut être orientée ou non, pondérée ou non.' },
          { id: 's9', text: 'Quelle structure est optimale pour implémenter une fonction "undo" (annuler) ?', question_type: 'multiple_choice', options: ['File (Queue)', 'Table de hachage', 'Pile (Stack)', 'Arbre AVL'], correct_answer: 2, points: 1, explanation: 'La pile permet d\'annuler dans l\'ordre inverse des actions : dernier ajouté, premier retiré (LIFO).' },
          { id: 's10', text: 'Quel algorithme de parcours utilise une file (Queue) ?', question_type: 'multiple_choice', options: ['DFS (Depth-First Search)', 'BFS (Breadth-First Search)', 'Tri topologique', 'Backtracking'], correct_answer: 1, points: 1, explanation: 'Le BFS explore niveau par niveau en utilisant une file pour gérer l\'ordre de visite.' }
        ],
        time_limit_minutes: 7,
        is_active: true
      }
    ];
    quizzes = addStatusToQuizzes(allQuizzes);
  }
}

// === FONCTION QUI CALCULE LE STATUT (✅ ▶️ 🔒) ===
function addStatusToQuizzes(allQuizzes) {
  // 1. On lit ce qui est sauvegardé dans le navigateur
  const saved = JSON.parse(localStorage.getItem('quiz_results') || '[]');
  console.log("📋 Résultats lus du localStorage:", saved);
  
  // 2. On crée une liste rapide des IDs terminés
  const completedIds = new Set(saved.map(r => r.quizId));
  
  // 3. On parcourt chaque quiz pour lui donner un statut
  return allQuizzes.map((quiz, index) => {
    let status = 'locked';
    let score = null;

    if (completedIds.has(quiz.id)) {
      status = 'completed';
      const res = saved.find(r => r.quizId === quiz.id);
      score = (res?.percentage || 0) + '%';
    } 
    else if (index === 0 || completedIds.has(allQuizzes[index - 1].id)) {
      status = 'available';
    }

    // ✅ Le console.log est MAINTENANT à l'intérieur de la boucle
    console.log(`📝 Quiz: ${quiz.title}, Status: ${status}, Score: ${score}`);

    return { ...quiz, status, score };
  });
}



// === NOUVELLE FONCTION : Filtrer les quiz selon la progression ===
function filterQuizzesByProgress(allQuizzes: any[]) {
  // Lire les résultats sauvegardés
  const savedResults = JSON.parse(localStorage.getItem('quiz_results') || '[]');
  
  // Créer un Set des IDs des quiz terminés
  const completedIds = new Set(savedResults.map((r: any) => r.quizId));
  
  // Filtrer : garder seulement le 1er quiz OU les quiz dont le précédent est terminé
  return allQuizzes.filter((quiz, index) => {
    // Le 1er quiz est toujours accessible
    if (index === 0) return true;
    
    // Les autres quiz sont accessibles seulement si le précédent est terminé
    const previousQuiz = allQuizzes[index - 1];
    return completedIds.has(previousQuiz.id);
  });
}

  // === 💾 SAUVEGARDE DES RÉSULTATS (Dashboard) ===
  function saveQuizResult() {
    if (!activeQuiz) return;
    
    const result = {
      id: Date.now().toString(),
      quizId: activeQuiz.id,
      quizTitle: activeQuiz.title,
      subject: activeQuiz.subject,
      date: new Date().toISOString(),
      dateFormatted: new Date().toLocaleDateString('fr-FR', { 
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' 
      }),
      score: score,
      totalQuestions: activeQuiz.questions.length,
      percentage: Math.round((score / activeQuiz.questions.length) * 100),
      timeLimit: activeQuiz.time_limit_minutes
    };

    try {
      const existing = JSON.parse(localStorage.getItem('quiz_results') || '[]');
      existing.unshift(result);
      if (existing.length > 50) existing.pop();
      localStorage.setItem('quiz_results', JSON.stringify(existing));
      console.log("✅ Résultat sauvegardé:", result);
    } catch (err) {
      console.warn("⚠️ Impossible de sauvegarder le résultat:", err);
    }
  }

  // === 🔀 FONCTION DE MÉLANGE (Fisher-Yates) ===
  function shuffleArray<T>(array: T[]): T[] {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // === FONCTIONS AUDIO ===
  function playWarningSound() {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      gainNode.gain.value = 0.3;
      
      oscillator.start();
      setTimeout(() => oscillator.stop(), 200);
    } catch (e) {
      console.warn("Audio non supporté:", e);
    }
  }

  // === NOTIFICATIONS FLOTTANTES ===
  function showTimerAlert(message: string, isCritical = false) {
    const alert = document.createElement('div');
    alert.className = `timer-alert ${isCritical ? 'critical' : ''}`;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
      if (alert.parentNode) {
        alert.parentNode.removeChild(alert);
      }
    }, 5000);
  }

  // === TIMER PRINCIPAL ===
  function startTimer(minutes: number) {
    timeRemaining = minutes * 60;
    totalTime = timeRemaining;
    isTimerRunning = true;
    isTimerPaused = false;
    
    hasWarned5min = false;
    hasWarned2min = false;
    hasWarned1min = false;
    
    if (timerInterval) clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
      if (isTimerPaused || timeRemaining === null) return;
      
      if (timeRemaining > 0) {
        timeRemaining--;
        
        if (timeRemaining === 300 && !hasWarned5min) {
          hasWarned5min = true;
          playWarningSound();
          showTimerAlert("⏱️ Il reste 5 minutes");
        }
        if (timeRemaining === 120 && !hasWarned2min) {
          hasWarned2min = true;
          playWarningSound();
          showTimerAlert("⏱️ Il reste 2 minutes");
        }
        if (timeRemaining === 60 && !hasWarned1min) {
          hasWarned1min = true;
          playWarningSound();
          showTimerAlert("⚠️ Il ne reste qu'1 minute !", true);
        }
        
        if (activeQuiz?.id) {
          localStorage.setItem(`timer_${activeQuiz.id}`, timeRemaining.toString());
        }
        
      } else if (timeRemaining === 0) {
        clearInterval(timerInterval);
        isTimerRunning = false;
        if (activeQuiz?.id) {
          localStorage.removeItem(`timer_${activeQuiz.id}`);
        }
        showTimerAlert("⏰ Temps écoulé ! Soumission automatique...", true);
        autoSubmitQuiz();
      }
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
      isTimerRunning = false;
      isTimerPaused = false;
    }
  }

  function pauseTimer() {
    if (!isTimerRunning || isTimerPaused) return;
    isTimerPaused = true;
    showTimerAlert("⏸️ Timer en pause");
  }

  function resumeTimer() {
    if (!isTimerRunning || !isTimerPaused) return;
    isTimerPaused = false;
    showTimerAlert("▶️ Timer repris");
  }

  function togglePause() {
    if (isTimerPaused) {
      resumeTimer();
    } else {
      pauseTimer();
    }
  }

  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  // === PERSISTANCE : Restaurer timer après refresh ===
  function restoreTimerIfNeeded(quiz: any): boolean {
    if (!quiz?.id) return false;
    
    const saved = localStorage.getItem(`timer_${quiz.id}`);
    if (saved && quiz.time_limit_minutes) {
      const remaining = parseInt(saved, 10);
      if (remaining > 0 && remaining <= quiz.time_limit_minutes * 60) {
        console.log("🔄 Timer restauré:", remaining);
        timeRemaining = remaining;
        totalTime = quiz.time_limit_minutes * 60;
        isTimerRunning = true;
        isTimerPaused = false;
        
        hasWarned5min = remaining <= 300;
        hasWarned2min = remaining <= 120;
        hasWarned1min = remaining <= 60;
        
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
          if (isTimerPaused || timeRemaining === null) return;
          if (timeRemaining > 0) {
            timeRemaining--;
            localStorage.setItem(`timer_${quiz.id}`, timeRemaining.toString());
          } else {
            clearInterval(timerInterval);
            localStorage.removeItem(`timer_${quiz.id}`);
            autoSubmitQuiz();
          }
        }, 1000);
        
        return true;
      }
    }
    return false;
  }

  // === ACTIONS UTILISATEUR ===
  function startQuiz(quiz: any) {
  //  1. NETTOYAGE RADICAL (empêche les timers fantômes)
  stopTimer();
  if (activeQuiz?.id) localStorage.removeItem(`timer_${activeQuiz.id}`);
  if (quiz?.id) localStorage.removeItem(`timer_${quiz.id}`);

  // 🔄 2. RESET COMPLET des variables d'état
  timeRemaining = null;
  totalTime = null;
  isTimerRunning = false;
  isTimerPaused = false;
  hasWarned5min = false;
  hasWarned2min = false;
  hasWarned1min = false;

  // 🔀 3. MÉLANGE ALÉATOIRE (Fisher-Yates)
  const shuffledQuestions = shuffleArray(quiz.questions).map(q => {
    const originalCorrectIndex = parseInt(q.correct_answer);
    const correctOptionValue = q.options[originalCorrectIndex];
    const newOptions = shuffleArray(q.options);
    const newCorrectIndex = newOptions.indexOf(correctOptionValue);
    return { ...q, options: newOptions, correct_answer: newCorrectIndex.toString() };
  });

  // 📦 4. INITIALISATION DU QUIZ
  activeQuiz = { ...quiz, questions: shuffledQuestions };
  currentQuestionIndex = 0;
  selectedAnswer = null;
  isAnswered = false;
  score = 0;
  quizFinished = false;
  answers = {};
  quizResult = null;

  // ️ 5. LANCEMENT DU TIMER FRAIS (sans restauration)
  if (quiz.time_limit_minutes) {
    startTimer(quiz.time_limit_minutes);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

  function backToList() {
    stopTimer();
    if (activeQuiz?.id) {
      localStorage.removeItem(`timer_${activeQuiz.id}`);
    }
    activeQuiz = null;
    fetchQuizzes();
  }

  function selectAnswer(index: number) {
    if (!isAnswered) {
      selectedAnswer = index;
      answers[activeQuiz.questions[currentQuestionIndex].id] = index;
    }
  }

  function validateAnswer() {
    if (selectedAnswer === null || isAnswered) return;
    isAnswered = true;
    const q = activeQuiz.questions[currentQuestionIndex];
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
      stopTimer();
      
      // 🪄 C'EST CETTE LIGNE QUI MANQUAIT !
      submitCurrentQuiz(); 
    }
  }

  function restartQuiz() {
    stopTimer();
    if (activeQuiz?.id) {
      localStorage.removeItem(`timer_${activeQuiz.id}`);
    }
    // Réinitialise TOUT l'état avant de relancer
    currentQuestionIndex = 0;
    selectedAnswer = null;
    isAnswered = false;
    score = 0;
    quizFinished = false;
    answers = {};
    quizResult = null;
    
    // Relance le quiz avec nouveau mélange + timer frais
    startQuiz(activeQuiz);
  }

  async function autoSubmitQuiz() {
    console.log("⏰ Temps écoulé! Soumission automatique...");
    if (selectedAnswer !== null && !isAnswered) {
      validateAnswer();
    }
    await submitCurrentQuiz();
  }

  async function submitCurrentQuiz() {
    if (!activeQuiz) return;
    
    try {
      saveQuizResult();
      
      const result = {
        score: score,
        total_questions: activeQuiz.questions.length,
        feedback: score === activeQuiz.questions.length ? 'Parfait ! 🌟' : score >= activeQuiz.questions.length / 2 ? 'Bon travail ! 👍' : 'Continuez à pratiquer ! 💪'
      };
      
      quizResult = result;
      quizFinished = true;
      stopTimer();
    } catch (err) {
      console.error("Erreur de soumission:", err);
    }
  }
  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
    if (audioContext) audioContext.close();
  });
</script>

<!-- === TIMER BADGE + PROGRESS + PAUSE (CENTRÉS & AGRANDIS) === -->
{#if activeQuiz && !quizFinished && activeQuiz.time_limit_minutes && timeRemaining !== null}
  <div class="timer-badge" class:warning={timeRemaining < 60}>
    <span class="timer-icon">⏱️</span>
    <span class="timer-value">{formatTime(timeRemaining)}</span>
  </div>
  
  <div class="timer-progress-container">
    <div 
      class="timer-progress-bar" 
      style="width: {totalTime ? (timeRemaining / totalTime) * 100 : 100}%"
      class:warning={timeRemaining < 60}
      class:critical={timeRemaining < 30}
    ></div>
  </div>
  
  <button 
    on:click={togglePause}
    class="timer-pause-btn"
    title={isTimerPaused ? "Reprendre le timer" : "Mettre en pause"}
  >
    {isTimerPaused ? '▶️ Reprendre' : '⏸️ Pause'}
  </button>
{/if}

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
          {score === activeQuiz.questions.length ? 'Parfait ! 🌟' : score >= activeQuiz.questions.length / 2 ? 'Bon travail ! 👍' : 'Continuez à pratiquer ! 💪'}
        </p>
        
        <div style="margin-bottom:1.5rem;">
          <button on:click={() => goto('/student/results')} 
            style="padding:0.6rem 1.2rem; background:#10b981; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600; margin:0 0.5rem;">
            📊 Voir mes résultats
          </button>
        </div>
        
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
            ✅ Valider la réponse
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
           <button 
  on:click={() => quiz.status !== 'locked' && startQuiz(quiz)}
  disabled={quiz.status === 'locked'}
  style="width:100%; padding:0.75rem; color:white; border:none; border-radius:8px; font-weight:600; cursor: {quiz.status === 'locked' ? 'not-allowed' : 'pointer'}; background: {quiz.status === 'completed' ? '#10b981' : quiz.status === 'available' ? '#3b82f6' : '#9ca3af'};">
  
  {#if quiz.status === 'completed'}
    ✅ Terminé ({quiz.score})
  {:else if quiz.status === 'available'}
    ▶️ Commencer
  {:else}
    🔒 Verrouillé
  {/if}
</button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}



<!-- === CSS AVANCÉ DU TIMER === -->
<style>
  /* === TIMER BADGE AGRANDI === */
  .timer-badge {
    position: fixed;
    top: 90px; /* Point d'ancrage */
    left: 50%;
    transform: translateX(-300%); /* Centrage parfait */
    background: #fff;
    padding: 0.8rem 2rem; /* Plus grand */
    border-radius: 9999px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.15); /* Ombre plus prononcée */
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 800; /* Police plus grasse */
    font-size: 1.5rem; /* Texte beaucoup plus grand */
    color: #1e40af;
    border: 3px solid #3b82f6; /* Bordure plus épaisse */
    z-index: 1000;
    transition: all 0.3s ease;
    animation: slideIn 0.3s ease-out;
  }

  .timer-badge.warning {
    background: #fef2f2;
    color: #dc2626;
    border-color: #ef4444;
    animation: pulse 1s infinite;
  }

  .timer-icon { 
    font-size: 1.8rem; /* Icône agrandie */
  }

  /* === BARRE DE PROGRESSION AGRANDIE === */
  .timer-progress-container {
    position: fixed;
    top: 145px; /* Décalé vers le bas pour éviter de toucher le badge */
    left: 55%;
    transform: translateX(-50%);
    width: 220px; /* Plus large */
    height: 8px; /* Plus épaisse */
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    z-index: 999;
  }

  .timer-progress-bar {
    height: 100%;
    background: #3b82f6;
    transition: width 0.3s linear, background 0.3s ease;
    border-radius: 4px;
  }

  .timer-progress-bar.warning { background: #f59e0b; }
  .timer-progress-bar.critical { 
    background: #ef4444; 
    animation: pulse-bar 0.5s infinite; 
  }

  @keyframes pulse-bar {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  /* === BOUTON PAUSE AGRANDI === */
  .timer-pause-btn {
    position: fixed;
    top: 105px; /* Décalé vers le bas */
    left: 60%;
    transform: translateX(260%);
    padding: 0.8rem 2rem; 
    background: #fff;
    border: 2px solid #6b7280;
    border-radius: 8px;
    font-size: 1rem; /* Texte plus lisible */
    font-weight: 900;
    color: #374151;
    cursor: pointer;
    z-index: 999;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }

  .timer-pause-btn:hover {
    background: #f3f4f6;
    border-color: #3b82f6;
    color: #3b82f6;
  }

  /* === NOTIFICATIONS FLOTTANTES AGRANDIES === */
  .timer-alert {
    position: fixed;
    top: 215px; /* Décalé vers le bas */
    left: 50%;
    transform: translateX(-50%);
    padding: 0.8rem 1.5rem;
    background: #fef3c7;
    border: 2px solid #f59e0b;
    border-radius: 8px;
    color: #92400e;
    font-weight: 700;
    font-size: 1rem;
    z-index: 1001;
    animation: slideInAlert 0.3s ease-out, fadeOutAlert 0.5s ease-in 4.5s forwards;
    box-shadow: 0 6px 12px rgba(245, 158, 11, 0.3);
  }

  .timer-alert.critical {
    background: #fef2f2;
    border-color: #ef4444;
    color: #991b1b;
  }

  /* === ANIMATIONS (Ajustées pour le centrage) === */
  @keyframes slideIn {
    from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
  }

  @keyframes pulse {
    0%, 100% { transform: translateX(-50%) scale(1); }
    50% { transform: translateX(-50%) scale(1.05); }
  }

  @keyframes slideInAlert {
    from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
  }

  @keyframes fadeOutAlert {
    to { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  }
</style>
