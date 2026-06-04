# Data fetching (server-cache, not global store)

```tsx
// TanStack Query: server data as a cache
const { data, isLoading, error } = useQuery({
  queryKey: ['orders', customerId],
  queryFn: () => api.getOrders(customerId),   // typed end-to-end
});

// mutation with invalidation
const mutation = useMutation({
  mutationFn: api.createOrder,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
});
```
Never store this in Redux. Client-only state -> local/context/store by scope.
