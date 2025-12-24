import http from './http'

export function createStory() {
  return http.post('/story/create', {})
}

export function continueStory(payload) {
  // payload: { story_id, user_text, rounds, mode }
  return http.post('/story/continue', payload)
}

export function getStory(storyId) {
  return http.get(`/story/${storyId}`)
}

export function compareStory(storyId) {
  return http.get('/metrics/compare', { params: { story_id: storyId } })
}

export function getStaticData() {
  return http.get('/story/static-data')
}
