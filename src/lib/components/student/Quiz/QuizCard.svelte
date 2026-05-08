<!-- src/lib/components/student/Quiz/QuizCard.svelte -->
<script lang="ts">
  export let quiz;
  export let onStart;
  
  let loading = false;
  
  function handleClick() {
    loading = true;
    onStart(quiz);
    loading = false;
  }
</script>

<div class="quiz-card">
  <h3>{quiz.title}</h3>
  <p class="subject">{quiz.subject}</p>
  <p>{quiz.description}</p>
  <div class="meta">
    <span>📝 {quiz.questions?.length || 0} questions</span>
    {#if quiz.time_limit_minutes}<span>⏱️ {quiz.time_limit_minutes} min</span>{/if}
  </div>
  <button on:click={handleClick} disabled={loading || !quiz.is_active}>
    {loading ? 'Chargement...' : 'Commencer'}
  </button>
</div>

<style>
  .quiz-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; background: #fff; }
  .subject { color: #3b82f6; font-weight: 500; }
  .meta { display: flex; gap: 1rem; margin: 1rem 0; font-size: 0.9rem; color: #6b7280; }
  button { width: 100%; padding: 0.75rem; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
