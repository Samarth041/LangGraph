## Message State
- predefined state schema provided by langgraph

```python
from langgraph.graph import MessageState
```
it is a Python class that define what the graph's state should look like

```python
class MessageState:
    message:list
```

whiche measn graph state must contain  a key named message that stores a list of chat messages


```python
def mock_llm(state:MessageState)
```

is equivalent to 
```python
def function(parameter:type) #typehint(or type annotation)
```

Eg:-
```python
def add(a:int,b:int):
    return a+b
```
---
# Graph API vs Functional API in LangGraph

| Feature | Graph API | Functional API |
|----------|-----------|----------------|
| Workflow definition | Explicit graph | Python functions |
| Nodes and edges | Manually defined | Implicit |
| Visualization | Very easy | Less explicit |
| Complex branching | Excellent | Good |
| Parallelization | Excellent | Easy using tasks |
| Cycles/loops | Very natural | Possible but less intuitive |
| Learning curve | Higher | Lower |
| Best for | Large agent systems | Simple workflows |

 Summary

- **Graph API** is ideal for building complex, multi-agent, and long-running workflows.
- **Functional API** is ideal for simple, sequential workflows and feels more like standard Python programming.

---

# add_messages
is a reducer provided by langraph which tells how to update the messages field in the state

"Whenever a node return new msg, append them to the existing converstaion history"
