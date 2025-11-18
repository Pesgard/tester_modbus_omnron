<script lang="ts">
    export let show = false;
    export let images: string[] = [];
    export let onClose = () => {};
  
    let carousel: HTMLDivElement | null = null;
    let btnLeft: HTMLButtonElement | null = null;
    let btnRight: HTMLButtonElement | null = null;
    let thumbs: HTMLElement[] = [];
  
    function left() {
      if (!carousel) return;
      const x =
        carousel.scrollLeft === 0
          ? carousel.clientWidth * carousel.childElementCount
          : carousel.scrollLeft - carousel.clientWidth;
      carousel.scroll(x, 0);
    }
  
    function right() {
      if (!carousel) return;
      const x =
        carousel.scrollLeft === carousel.scrollWidth - carousel.clientWidth
          ? 0
          : carousel.scrollLeft + carousel.clientWidth;
      carousel.scroll(x, 0);
    }
  
    function goTo(index: number) {
      if (carousel) carousel.scroll(carousel.clientWidth * index, 0);
    }
  </script>
  
  {#if show}
  <div class="fixed inset-0 bg-black/60 z-50" onclick={onClose}></div>
  
  <div
    class="fixed inset-0 z-50 grid place-items-center p-4"
  >
    <div class="card p-4 w-full max-w-3xl bg-surface-100 relative">
      
      <!-- Cerrar -->
      <button
        class="absolute top-2 right-2 btn-icon preset-filled"
        onclick={onClose}
      >
        ✕
      </button>
  
      <!-- Carousel -->
      <div class="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
  
        <!-- Izquierda -->
        <button
          bind:this={btnLeft}
          onclick={left}
          class="btn-icon preset-filled"
        >
          ←
        </button>
  
        <!-- Contenedor de imágenes grandes -->
        <div
          bind:this={carousel}
          class="snap-x snap-mandatory scroll-smooth flex overflow-x-auto rounded-container"
        >
          {#each images as img, i}
            <img
              class="snap-center w-[900px] max-h-[70vh] object-contain rounded-container"
              src={img}
              alt={`img-${i}`}
            />
          {/each}
        </div>
  
        <!-- Derecha -->
        <button
          bind:this={btnRight}
          onclick={right}
          class="btn-icon preset-filled"
        >
          →
        </button>
      </div>
  
      <!-- Miniaturas -->
      <div class="mt-4 grid grid-cols-6 gap-2">
        {#each images as img, i}
          <button
            bind:this={thumbs[i]}
            onclick={() => goTo(i)}
            class="hover:brightness-125"
          >
            <img
              class="rounded-container"
              src={img}
              alt={`thumb-${i}`}
            />
          </button>
        {/each}
      </div>
  
    </div>
  </div>
  {/if}
  
  <style>
    /* Evita que el clic en el modal cierre por accidente */
    .card {
      pointer-events: auto;
    }
  </style>
  