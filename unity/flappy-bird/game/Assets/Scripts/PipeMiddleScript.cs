using UnityEngine;

public class PipeMiddleScript : MonoBehaviour
{
    public LogicScript logic;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // looks for first gameObject in heirarchy with tag "Logic"
        // looks for gameComponent script  LogicScript
        // if found, put into reference slot, ie logic
        // same as drag/drop element instead done at runtime
        logic = GameObject.FindGameObjectWithTag("Logic").GetComponent<LogicScript>();  // use shit from logicScript, needs to have tag in logic Manager
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.gameObject.layer == 3)    // collision happened on bird layer ie with bird
        {
            logic.addScore(1);
        }
        

    }
}
