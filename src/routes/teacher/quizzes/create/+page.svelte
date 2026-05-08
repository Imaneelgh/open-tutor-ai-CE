<script lang="ts">
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores';
  import { onMount, getContext } from 'svelte';

  const i18n = getContext('i18n');
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  let loading = false;
  let error = null;
  let success = false;

  // État du formulaire
  let title = '';
  let subject = '';
  let description = '';
  let timeLimit = 10;
  let questions = [
    { text: '', question_type: 'multiple_choice', options: ['', ''], correct_answer: 0, explanation: '' }
  ];

  function addQuestion() {
    questions = [...questions, { text: '', question_type: 'multiple_choice', options: ['', ''], correct_answer: 0, explanation: '' }];
  }

  function removeQuestion(index) {
    if (questions.length > 1) questions = questions.filter((_, i) => i !== index);
  }

  function addOption(qIndex) {
    const newQs = [...questions];
    newQs[qIndex].options = [...newQs[qIndex].options, ''];
    questions = newQs;
  }

  function removeOption(qIndex, optIndex) {
    const newQs = [...questions];
    newQs[qIndex].options = newQs[qIndex].options.filter((_, i) => i !== optIndex);
    if (newQs[qIndex].correct_answer >= newQs[qIndex].options.length) {
      newQs[qIndex].correct_answer = Math.max(0, newQs[qIndex].options.length - 1);
    }
    questions = newQs;
  }

  async function handleSubmit() {
    if (!title || !subject || questions.some(q => !q.text)) {
      error = "Veuillez remplir tous les champs obligatoires";
      return;
    }

    loading = true;
    error = null;
    success = false;

    try {
      const payload = {
        title, subject, description,
        time_limit_minutes: parseInt(timeLimit) || 10,
        is_active: true,
        questions: questions.map(q => ({
          ...q,
          correct_answer: parseInt(q.correct_answer) || 0
        }))
      };

      const res = await fetch(`${API_BASE}/api/v1/quizzes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Échec de la création');
      success = true;
      // Reset
      title = ''; subject = ''; description = ''; timeLimit = 10;
      questions = [{ text: '', question_type: 'multiple_choice', options: ['', ''], correct_answer: 0, explanation: '' }];
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div style="padding: 2rem; max-width: 900px; margin: 0 auto;">
  <button on:click={() => goto('/teacher/dashboard')} style="margin-bottom:1rem; color:#3b82f6; background:none; border:none; cursor:pointer; font-weight:500;">← Retour</button>
  <h1 style="font-size:1.8rem; margin:0 0 1.5rem 0;">📝 Créer un Quiz</h1>

  {#if success}
    <div style="background:#d1fae5; color:#065f46; padding:1rem; border-radius:8px; margin-bottom:1rem; text-align:center;">
      ✅ Quiz créé avec succès ! Il est maintenant visible par les étudiants.
    </div>
  {/if}
  {#if error}
    <div style="background:#fef2f2; color:#991b1b; padding:1rem; border-radius:8px; margin-bottom:1rem;">⚠️ {error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit} style="display:flex; flex-direction:column; gap:1.5rem;">
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
      <div>
        <label style="display:block; margin-bottom:0.5rem; font-weight:500;">Titre *</label>
        <input bind:value={title} required style="width:100%; padding:0.75rem; border:1px solid #d1d5db; border-radius:6px;" />
      </div>
      <div>
        <label style="display:block; margin-bottom:0.5rem; font-weight:500;">Matière *</label>
        <input bind:value={subject} required style="width:100%; padding:0.75rem; border:1px solid #d1d5db; border-radius:6px;" />
      </div>
    </div>
    <div>
      <label style="display:block; margin-bottom:0.5rem; font-weight:500;">Description</label>
      <textarea bind:value={description} rows="3" style="width:100%; padding:0.75rem; border:1px solid #d1d5db; border-radius:6px;"></textarea>
    </div>
    <div style="width:200px;">
      <label style="display:block; margin-bottom:0.5rem; font-weight:500;">Temps limite (min)</label>
      <input type="number" bind:value={timeLimit} min="1" style="width:100%; padding:0.75rem; border:1px solid #d1d5db; border-radius:6px;" />
    </div>

    <div style="border-top:1px solid #e5e7eb; padding-top:1rem;">
      <h2 style="margin:0 0 1rem 0;">Questions</h2>
      {#each questions as q, qIndex}
        <div style="background:#f9fafb; padding:1rem; border-radius:8px; margin-bottom:1rem; border:1px solid #e5e7eb;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <span style="font-weight:600;">Question {qIndex + 1}</span>
            <button type="button" on:click={() => removeQuestion(qIndex)} style="color:#ef4444; background:none; border:none; cursor:pointer;">Supprimer</button>
          </div>
          
          <label style="display:block; margin-bottom:0.5rem; font-size:0.9rem;">Énoncé *</label>
          <textarea bind:value={questions[qIndex].text} rows="2" required style="width:100%; padding:0.5rem; border:1px solid #d1d5db; border-radius:6px; margin-bottom:0.75rem;"></textarea>
          
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
            <div>
              <label style="font-size:0.9rem;">Type</label>
              <select bind:value={questions[qIndex].question_type} style="width:100%; padding:0.5rem; border:1px solid #d1d5db; border-radius:6px;">
                <option value="multiple_choice">QCM</option>
                <option value="true_false">Vrai/Faux</option>
              </select>
            </div>
            <div>
              <label style="font-size:0.9rem;">Réponse correcte (index 0,1,2...)</label>
              <input type="number" bind:value={questions[qIndex].correct_answer} min="0" style="width:100%; padding:0.5rem; border:1px solid #d1d5db; border-radius:6px;" />
            </div>
          </div>

          <label style="display:block; margin-bottom:0.5rem; font-size:0.9rem;">Options</label>
          {#each q.options as opt, optIndex}
            <div style="display:flex; gap:0.5rem; margin-bottom:0.5rem;">
              <input bind:value={questions[qIndex].options[optIndex]} placeholder="Option {optIndex + 1}" style="flex:1; padding:0.5rem; border:1px solid #d1d5db; border-radius:6px;" />
              <button type="button" on:click={() => removeOption(qIndex, optIndex)} style="color:#ef4444; background:none; border:none; cursor:pointer;">✕</button>
            </div>
          {/each}
          <button type="button" on:click={() => addOption(qIndex)} style="font-size:0.85rem; color:#3b82f6; background:none; border:none; cursor:pointer; margin-top:0.25rem;">+ Ajouter option</button>
          
          <label style="display:block; margin-top:0.75rem; margin-bottom:0.5rem; font-size:0.9rem;">Explication (optionnel)</label>
          <textarea bind:value={questions[qIndex].explanation} rows="2" style="width:100%; padding:0.5rem; border:1px solid #d1d5db; border-radius:6px;"></textarea>
        </div>
      {/each}
      
      <button type="button" on:click={addQuestion} style="padding:0.75rem; background:#e5e7eb; color:#374151; border:none; border-radius:8px; cursor:pointer; font-weight:500; width:100%;">+ Ajouter une question</button>
    </div>

    <button type="submit" disabled={loading} style="padding:1rem; background:#3b82f6; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600; font-size:1.1rem; margin-top:1rem;">
      {loading ? 'Création...' : '🚀 Publier le Quiz'}
    </button>
  </form>
</div>
