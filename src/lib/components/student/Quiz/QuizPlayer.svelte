<!-- src/lib/components/student/Quiz/QuizPlayer.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  
  export let quiz;
  export let onSubmit;
  export let onComplete;
  
  // Variables Svelte 4 - PAS de $state
  let currentQuestionIndex = 0;
  let answers: Record<string, any> = {};
  let submitted = false;
  let quizResult: any = null;
  let timer: any = null;
  
  // Réactivité Svelte 4 avec $:
  $: currentQuestion = quiz.questions?.[currentQuestionIndex];
  $: totalQuestions = quiz.questions?.length || 0;
  $: progressPercent = totalQuestions ? ((currentQuestionIndex + 1) / totalQuestions * 100) : 0;
  
  onMount(() => {
    // Cleanup au démontage
    return () => {
      if (timer) clearInterval(timer);
    };
  });
  
  function selectAnswer(questionId: string, answer: any) {
    answers = { ...answers, [questionId]: answer };
  }
  
  function nextQuestion() {
    if (currentQuestionIndex < totalQuestions - 1) {
      currentQuestionIndex++;
    }
  }
  
  function prevQuestion() {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
    }
  }
  
  async function submitQuiz() {
    submitted = true;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    try {
      quizResult = await onSubmit({
        quiz_id: quiz.id,
        answers: answers
      });
    } catch (error) {
      console.error("Erreur de soumission:", error);
    }
  }
  
  function restartQuiz() {
    submitted = false;
    currentQuestionIndex = 0;
    answers = {};
    quizResult = null;
  }
  
  function formatTime(seconds: number) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }
</script>

{#if submitted && quizResult}
  <div class="results">
    <h2>🎉 Quiz Terminé !</h2>
    <div class="score">{quizResult.score}%</div>
    <p>{quizResult.feedback}</p>
    <div class="actions">
      <button on:click={onComplete}>Retour aux quiz</button>
      <button on:click={restartQuiz}>Recommencer</button>
    </div>
  </div>
{:else}
  <div class="quiz-player">
    <header>
      <h2>{quiz.title}</h2>
      <p>Question {currentQuestionIndex + 1} / {totalQuestions}</p>
      <div class="progress-bar"><div class="progress-fill" style="width: {progressPercent}%"></div></div>
    </header>
    
    {#if currentQuestion}
      <div class="question">
        <p class="text">{currentQuestion.text}</p>
        
        {#if currentQuestion.question_type === 'multiple_choice'}
          {#each currentQuestion.options as option, index}
            <label class="option">
              <input type="radio" name={currentQuestion.id} value={index}
                on:change={() => selectAnswer(currentQuestion.id, index)}
                checked={answers[currentQuestion.id] === index} />
              {option}
            </label>
          {/each}
        {:else if currentQuestion.question_type === 'true_false'}
          <label class="option">
            <input type="radio" name={currentQuestion.id} value="true"
              on:change={() => selectAnswer(currentQuestion.id, 'true')}
              checked={answers[currentQuestion.id] === 'true'} /> Vrai
          </label>
          <label class="option">
            <input type="radio" name={currentQuestion.id} value="false"
              on:change={() => selectAnswer(currentQuestion.id, 'false')}
              checked={answers[currentQuestion.id] === 'false'} /> Faux
          </label>
        {/if}
      </div>
      
      <footer>
        <button on:click={prevQuestion} disabled={currentQuestionIndex === 0}>← Précédent</button>
        {#if currentQuestionIndex === totalQuestions - 1}
          <button on:click={submitQuiz}>Soumettre ✓</button>
        {:else}
          <button on:click={nextQuestion}>Suivant →</button>
        {/if}
      </footer>
    {:else}
      <p>Aucune question disponible</p>
    {/if}
  </div>
{/if}

<style>
  .quiz-player, .results { max-width: 800px; margin: 0 auto; padding: 2rem; }
  header { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e5e7eb; }
  .progress-bar { height: 6px; background: #e5e7eb; border-radius: 3px; margin-top: 0.5rem; }
  .progress-fill { height: 100%; background: #3b82f6; transition: width 0.3s; }
  .question { margin: 2rem 0; }
  .text { font-size: 1.2rem; margin-bottom: 1.5rem; font-weight: 500; }
  .option { display: block; padding: 1rem; margin: 0.5rem 0; border: 2px solid #e5e7eb; border-radius: 8px; cursor: pointer; }
  .option:hover { border-color: #3b82f6; }
  footer { display: flex; justify-content: space-between; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; }
  button { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; background: #3b82f6; color: white; font-weight: 500; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
  .results { text-align: center; }
  .score { font-size: 3rem; font-weight: bold; color: #3b82f6; margin: 1rem 0; }
</style>
