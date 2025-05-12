export class TreeNode {
    constructor(name) {
      this.name = name;
      this.children = [];
    }
  
    addChild(child) {
      this.children.push(child);
    }
  }