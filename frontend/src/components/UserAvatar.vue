<template>
  <img
    :src="src || '/api/user/avatars/default.png'"
    :style="{ width: size + 'px', height: size + 'px' }"
    class="user-avatar-img"
  />
</template>

<script setup>
defineProps({
  src: { type: String, default: '' },
  size: { type: Number, default: 36 }
})
</script>

<style scoped>
.user-avatar-img {
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
</style>
