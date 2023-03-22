package util

type semaphore struct {
	semC chan struct{}
}

func NewSemaphore(maxConcurrency int) *semaphore {
	return &semaphore{
		semC: make(chan struct{}, maxConcurrency),
	}
}
func (s *semaphore) Acquire() {
	s.semC <- struct{}{}
}
func (s *semaphore) Release() {
	<-s.semC
}
